// notification_service/main.go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "time"

    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/session"
    "github.com/aws/aws-sdk-go/service/sns"
    "github.com/aws/aws-sdk-go/service/ses"
    "github.com/gorilla/mux"
    "google.golang.org/api/firebase"
    firebase_messaging "firebase.google.com/go/messaging"
)

type NotificationType string

const (
    TypeSMS      NotificationType = "sms"
    TypeEmail    NotificationType = "email"
    TypePush     NotificationType = "push"
    TypeAlert    NotificationType = "alert"
)

type Recipient struct {
    UserID     string `json:"user_id"`
    Email      string `json:"email,omitempty"`
    PhoneNumber string `json:"phone_number,omitempty"`
    DeviceToken string `json:"device_token,omitempty"`
}

type NotificationRequest struct {
    Type        NotificationType `json:"type"`
    Recipients  []Recipient      `json:"recipients"`
    Title       string           `json:"title"`
    Message     string           `json:"message"`
    Priority    string           `json:"priority"` // high, normal
    Data        map[string]interface{} `json:"data,omitempty"`
    TemplateID  string           `json:"template_id,omitempty"`
}

type NotificationResponse struct {
    Success     bool     `json:"success"`
    MessageIDs  []string `json:"message_ids,omitempty"`
    FailedRecipients []string `json:"failed_recipients,omitempty"`
    Timestamp   string   `json:"timestamp"`
}

type NotificationService struct {
    snsClient *sns.SNS
    sesClient *ses.SES
    fcmClient *firebase_messaging.Client
}

func NewNotificationService() (*NotificationService, error) {
    // Initialize AWS session
    sess, err := session.NewSession(&aws.Config{
        Region: aws.String(os.Getenv("AWS_REGION")),
    })
    if err != nil {
        return nil, fmt.Errorf("failed to create AWS session: %v", err)
    }

    // Initialize Firebase for push notifications
    ctx := context.Background()
    app, err := firebase.NewApp(ctx, nil)
    if err != nil {
        return nil, fmt.Errorf("failed to initialize Firebase: %v", err)
    }

    fcmClient, err := app.Messaging(ctx)
    if err != nil {
        return nil, fmt.Errorf("failed to get FCM client: %v", err)
    }

    return &NotificationService{
        snsClient: sns.New(sess),
        sesClient: ses.New(sess),
        fcmClient: fcmClient,
    }, nil
}

func (s *NotificationService) sendSMS(recipient Recipient, message string) (string, error) {
    input := &sns.PublishInput{
        Message:     aws.String(message),
        PhoneNumber: aws.String(recipient.PhoneNumber),
        MessageAttributes: map[string]*sns.MessageAttributeValue{
            "AWS.SNS.SMS.SMSType": {
                DataType:    aws.String("String"),
                StringValue: aws.String("Transactional"),
            },
        },
    }

    result, err := s.snsClient.Publish(input)
    if err != nil {
        return "", err
    }

    return *result.MessageId, nil
}

func (s *NotificationService) sendEmail(recipient Recipient, subject, body string) (string, error) {
    input := &ses.SendEmailInput{
        Destination: &ses.Destination{
            ToAddresses: []*string{aws.String(recipient.Email)},
        },
        Message: &ses.Message{
            Body: &ses.Body{
                Text: &ses.Content{
                    Charset: aws.String("UTF-8"),
                    Data:    aws.String(body),
                },
            },
            Subject: &ses.Content{
                Charset: aws.String("UTF-8"),
                Data:    aws.String(subject),
            },
        },
        Source: aws.String(os.Getenv("EMAIL_SENDER")),
    }

    result, err := s.sesClient.SendEmail(input)
    if err != nil {
        return "", err
    }

    return *result.MessageId, nil
}

func (s *NotificationService) sendPushNotification(recipient Recipient, title, body string, data map[string]interface{}) error {
    message := &firebase_messaging.Message{
        Token: recipient.DeviceToken,
        Notification: &firebase_messaging.Notification{
            Title: title,
            Body:  body,
        },
        Data: data,
        Android: &firebase_messaging.AndroidConfig{
            Priority: "high",
            Notification: &firebase_messaging.AndroidNotification{
                Icon: "ic_notification",
            },
        },
        APNS: &firebase_messaging.APNSConfig{
            Payload: &firebase_messaging.APNSPayload{
                Aps: &firebase_messaging.Aps{
                    Alert: &firebase_messaging.ApsAlert{
                        Title: title,
                        Body:  body,
                    },
                    Sound: "default",
                },
            },
        },
    }

    _, err := s.fcmClient.Send(context.Background(), message)
    return err
}

func (s *NotificationService) sendNotification(req NotificationRequest) (*NotificationResponse, error) {
    response := &NotificationResponse{
        Success:          true,
        MessageIDs:       make([]string, 0),
        FailedRecipients: make([]string, 0),
        Timestamp:        time.Now().UTC().Format(time.RFC3339),
    }

    for _, recipient := range req.Recipients {
        var messageID string
        var err error

        switch req.Type {
        case TypeSMS:
            messageID, err = s.sendSMS(recipient, req.Message)
        case TypeEmail:
            messageID, err = s.sendEmail(recipient, req.Title, req.Message)
        case TypePush:
            err = s.sendPushNotification(recipient, req.Title, req.Message, req.Data)
            messageID = fmt.Sprintf("push_%d", time.Now().UnixNano())
        default:
            response.FailedRecipients = append(response.FailedRecipients, recipient.UserID)
            continue
        }

        if err != nil {
            log.Printf("Failed to send %s to recipient %s: %v", req.Type, recipient.UserID, err)
            response.FailedRecipients = append(response.FailedRecipients, recipient.UserID)
            response.Success = false
        } else {
            if messageID != "" {
                response.MessageIDs = append(response.MessageIDs, messageID)
            }
        }
    }

    return response, nil
}

func (s *NotificationService) sendNotificationHandler(w http.ResponseWriter, r *http.Request) {
    var req NotificationRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    response, err := s.sendNotification(req)
    if err != nil {
        log.Printf("Failed to send notifications: %v", err)
        http.Error(w, "Failed to send notifications", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func main() {
    service, err := NewNotificationService()
    if err != nil {
        log.Fatalf("Failed to initialize notification service: %v", err)
    }

    r := mux.NewRouter()
    r.HandleFunc("/v1/notifications/send", service.sendNotificationHandler).Methods("POST")
    r.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
    }).Methods("GET")

    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    log.Printf("Notification Service starting on port %s", port)
    log.Fatal(http.ListenAndServe(":"+port, r))
}
