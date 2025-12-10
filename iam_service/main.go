# iam_service/main.go
package main

import (
    "context"
    "crypto/sha256"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "time"

    "github.com/golang-jwt/jwt/v4"
    "github.com/gorilla/mux"
    "golang.org/x/crypto/bcrypt"
    "google.golang.org/api/idtoken"
)

type User struct {
    ID           string    `json:"id"`
    Email        string    `json:"email"`
    PasswordHash string    `json:"password_hash"`
    CreatedAt    time.Time `json:"created_at"`
    LastLogin    time.Time `json:"last_login"`
}

type TrustFactors struct {
    MFA        float64 `json:"mfa"`        // φ₁: 0.35 weight
    Device     float64 `json:"device"`     // φ₂: 0.20 weight
    Location   float64 `json:"location"`   // φ₃: 0.15 weight
    Behavior   float64 `json:"behavior"`   // φ₄: 0.20 weight
    Time       float64 `json:"time"`       // φ₅: 0.10 weight
}

type AuthRequest struct {
    Email    string `json:"email"`
    Password string `json:"password"`
    MFACode  string `json:"mfa_code"`
    DeviceID string `json:"device_id"`
}

type AuthResponse struct {
    Token       string  `json:"token"`
    TrustScore  float64 `json:"trust_score"`
    ExpiresAt   int64   `json:"expires_at"`
}

type Claims struct {
    UserID     string  `json:"user_id"`
    TrustScore float64 `json:"trust_score"`
    jwt.RegisteredClaims
}

type IAMService struct {
    jwtSecret []byte
}

func NewIAMService() *IAMService {
    return &IAMService{
        jwtSecret: []byte(os.Getenv("JWT_SECRET_KEY")),
    }
}

func (s *IAMService) calculateTrustScore(factors TrustFactors) float64 {
    // T(u,r,t) = Σ w_i × φ_i(u,r,t)
    score := 0.35*factors.MFA + 
             0.20*factors.Device + 
             0.15*factors.Location + 
             0.20*factors.Behavior + 
             0.10*factors.Time
    
    // Ensure score is between 0 and 1
    if score > 1.0 {
        return 1.0
    }
    if score < 0.0 {
        return 0.0
    }
    return score
}

func (s *IAMService) authenticateUser(req AuthRequest) (*AuthResponse, error) {
    // Validate user credentials (simplified)
    user, err := getUserByEmail(req.Email)
    if err != nil {
        return nil, fmt.Errorf("invalid credentials")
    }

    // Verify password
    if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(req.Password)); err != nil {
        return nil, fmt.Errorf("invalid credentials")
    }

    // Verify MFA (simplified)
    mfaValid := verifyMFA(req.Email, req.MFACode)
    if !mfaValid {
        return nil, fmt.Errorf("invalid MFA code")
    }

    // Calculate trust factors
    factors := TrustFactors{
        MFA:      0.95, // Simplified - would be dynamic in real implementation
        Device:   0.90,
        Location: 0.85,
        Behavior: 0.80,
        Time:     0.75,
    }

    trustScore := s.calculateTrustScore(factors)
    
    // Require minimum trust score
    if trustScore < 0.75 {
        return nil, fmt.Errorf("insufficient trust score: %.2f", trustScore)
    }

    // Generate JWT token
    expirationTime := time.Now().Add(15 * time.Minute)
    claims := &Claims{
        UserID:     user.ID,
        TrustScore: trustScore,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(expirationTime),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            Subject:   user.Email,
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    tokenString, err := token.SignedString(s.jwtSecret)
    if err != nil {
        return nil, fmt.Errorf("could not generate token: %v", err)
    }

    return &AuthResponse{
        Token:      tokenString,
        TrustScore: trustScore,
        ExpiresAt:  expirationTime.Unix(),
    }, nil
}

func (s *IAMService) loginHandler(w http.ResponseWriter, r *http.Request) {
    var req AuthRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    response, err := s.authenticateUser(req)
    if err != nil {
        log.Printf("Authentication failed for %s: %v", req.Email, err)
        http.Error(w, err.Error(), http.StatusUnauthorized)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func (s *IAMService) validateTokenHandler(w http.ResponseWriter, r *http.Request) {
    tokenString := r.Header.Get("Authorization")
    if tokenString == "" {
        http.Error(w, "Authorization header required", http.StatusUnauthorized)
        return
    }

    claims := &Claims{}
    token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
        return s.jwtSecret, nil
    })

    if err != nil || !token.Valid {
        http.Error(w, "Invalid token", http.StatusUnauthorized)
        return
    }

    response := map[string]interface{}{
        "valid":      true,
        "user_id":    claims.UserID,
        "trust_score": claims.TrustScore,
        "expires_at": claims.ExpiresAt.Unix(),
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func main() {
    service := NewIAMService()
    
    r := mux.NewRouter()
    r.HandleFunc("/v1/auth/login", service.loginHandler).Methods("POST")
    r.HandleFunc("/v1/auth/validate", service.validateTokenHandler).Methods("GET")
    r.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
    }).Methods("GET")

    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    log.Printf("IAM Service starting on port %s", port)
    log.Fatal(http.ListenAndServe(":"+port, r))
}

// Mock functions - would be replaced with actual database calls
func getUserByEmail(email string) (*User, error) {
    // This would query a database in real implementation
    passwordHash, _ := bcrypt.GenerateFromPassword([]byte("password123"), bcrypt.DefaultCost)
    return &User{
        ID:           fmt.Sprintf("%x", sha256.Sum256([]byte(email)))[:16],
        Email:        email,
        PasswordHash: string(passwordHash),
        CreatedAt:    time.Now(),
        LastLogin:    time.Now(),
    }, nil
}

func verifyMFA(email, code string) bool {
    // This would verify against an MFA service
    return code == "123456" // Simplified for example
}
