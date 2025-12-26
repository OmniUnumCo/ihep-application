'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Target, Briefcase, GraduationCap, FlaskConical, Users, X } from 'lucide-react'

interface Opportunity {
    title: string
    company?: string
    provider?: string
    institution?: string
    pay?: string
    compensation?: string
    hours?: string
    duration?: string
    commitment?: string
    skills?: string[]
    location?: string
    urgency?: string
    outcome?: string
    cost?: string
    criteria?: string
    description?: string
    matchScore?: number
}

const gigOpportunities: Opportunity[] = [
    {
        title: "Customer Service Representative - Remote",
        company: "TeleCare Solutions",
        pay: "$18-22/hour",
        hours: "20-40 hrs/week",
        skills: ["Customer Service", "Communication", "Problem Solving"],
        location: "Remote",
        urgency: "Hiring now"
    },
    {
        title: "Delivery Driver",
        company: "QuickShip Logistics",
        pay: "$20-25/hour + tips",
        hours: "Flexible scheduling",
        skills: ["Driving", "Time Management", "Customer Service"],
        location: "Miami, FL",
        urgency: "High demand"
    },
    {
        title: "Data Entry Specialist",
        company: "AdminPro Services",
        pay: "$16-20/hour",
        hours: "Part-time/Full-time",
        skills: ["Typing", "Attention to Detail", "Microsoft Office"],
        location: "Remote",
        urgency: "Multiple positions"
    },
    {
        title: "Healthcare Support Worker",
        company: "Community Health Partners",
        pay: "$22-28/hour",
        hours: "Full-time",
        skills: ["Healthcare", "Communication", "Empathy"],
        location: "Miami, FL",
        urgency: "Immediate start"
    },
    {
        title: "Social Media Assistant",
        company: "Digital Growth Agency",
        pay: "$17-22/hour",
        hours: "20-30 hrs/week",
        skills: ["Social Media", "Writing", "Creativity"],
        location: "Remote",
        urgency: "Contract position"
    }
]

const trainingPrograms: Opportunity[] = [
    {
        title: "Certified Peer Specialist Training",
        provider: "IHEP Academy",
        duration: "8 weeks",
        commitment: "Part-time (10 hrs/week)",
        outcome: "State certification + job placement",
        cost: "Free (grant-funded)"
    },
    {
        title: "Healthcare Navigation Certificate",
        provider: "Pacific Clinics Training Institute",
        duration: "40 hours + 4 coaching sessions",
        commitment: "Self-paced online",
        outcome: "Health Navigator credential",
        cost: "Scholarship available"
    },
    {
        title: "Digital Skills Bootcamp",
        provider: "Tech Forward Program",
        duration: "12 weeks",
        commitment: "Evening classes",
        outcome: "IT support certification",
        cost: "Income-based sliding scale"
    },
    {
        title: "Community Health Worker Training",
        provider: "Public Health Institute",
        duration: "6 weeks",
        commitment: "Weekends",
        outcome: "CHW certification + internship",
        cost: "Free with work commitment"
    }
]

const researchStudies: Opportunity[] = [
    {
        title: "Digital Health Engagement Study",
        institution: "University of Miami School of Medicine",
        compensation: "$500 stipend",
        commitment: "3 months (2 hrs/week)",
        criteria: "Living with chronic condition, smartphone user",
        description: "Help improve digital health tools through feedback and testing"
    },
    {
        title: "Peer Support Effectiveness Research",
        institution: "IHEP Research Division",
        compensation: "$300 gift card",
        commitment: "6-week program",
        criteria: "Interested in peer support, willingness to share experiences",
        description: "Evaluate new peer navigation approaches"
    },
    {
        title: "Community Health Navigator Trial",
        institution: "Johns Hopkins Bloomberg School",
        compensation: "$750 + training",
        commitment: "12 weeks",
        criteria: "Community connection, basic health knowledge",
        description: "Test innovative community health navigation model"
    }
]

export default function OpportunitiesPage() {
    const [skills, setSkills] = useState<string[]>([])
    const [skillInput, setSkillInput] = useState('')
    const [name, setName] = useState('')
    const [location, setLocation] = useState('')
    const [availability, setAvailability] = useState('full-time')
    const [interests, setInterests] = useState('')
    const [experience, setExperience] = useState('entry')
    const [showResults, setShowResults] = useState(false)

    const [gigMatches, setGigMatches] = useState<Opportunity[]>([])
    const [trainingMatches, setTrainingMatches] = useState<Opportunity[]>([])
    const [researchMatches, setResearchMatches] = useState<Opportunity[]>([])
    const [navigatorScore, setNavigatorScore] = useState(0)
    const [error, setError] = useState('')
    const [isSearching, setIsSearching] = useState(false)

    const addSkill = () => {
        const skill = skillInput.trim()
        if (skill && !skills.includes(skill)) {
            setSkills([...skills, skill])
            setSkillInput('')
        }
    }

    const removeSkill = (skillToRemove: string) => {
        setSkills(skills.filter(s => s !== skillToRemove))
    }

    const calculateMatchScore = (opportunity: Opportunity) => {
        let score = 50

        // Skill matching
        if (opportunity.skills) {
            const matchedSkills = opportunity.skills.filter(skill =>
                skills.some(userSkill =>
                    skill.toLowerCase().includes(userSkill.toLowerCase()) ||
                    userSkill.toLowerCase().includes(skill.toLowerCase())
                )
            )
            score += (matchedSkills.length / opportunity.skills.length) * 40
        }

        // Location matching
        if (opportunity.location) {
            if (opportunity.location === "Remote" ||
                opportunity.location.toLowerCase().includes(location.toLowerCase())) {
                score += 20
            }
        }

        // Random variation
        score += (Math.random() - 0.5) * 10

        return Math.round(Math.min(99, Math.max(50, score)))
    }

    const assessNavigatorFit = () => {
        let score = 60

        const interestsLower = interests.toLowerCase()
        const navigatorKeywords = ['help', 'support', 'community', 'healthcare', 'peer', 'assist', 'guide', 'navigate']
        const matchedKeywords = navigatorKeywords.filter(kw => interestsLower.includes(kw))
        score += matchedKeywords.length * 5

        if (skills.some(s => s.toLowerCase().includes('communication') ||
            s.toLowerCase().includes('customer service') ||
            s.toLowerCase().includes('empathy'))) {
            score += 15
        }

        return Math.round(Math.min(99, Math.max(50, score)))
    }

    const handleFindOpportunities = () => {
        setError('')

        if (skills.length === 0) {
            setError('Please add at least one skill to find matching opportunities')
            return
        }

        setIsSearching(true)

        // Simulate search delay for better UX
        setTimeout(() => {
            // Calculate matches
            const gigs = gigOpportunities
                .map(opp => ({ ...opp, matchScore: calculateMatchScore(opp) }))
                .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))
                .slice(0, 5)

            const training = trainingPrograms
                .map(prog => ({ ...prog, matchScore: calculateMatchScore(prog) }))
                .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))

            const research = researchStudies
                .map(study => ({ ...study, matchScore: calculateMatchScore(study) }))
                .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))

            setGigMatches(gigs)
            setTrainingMatches(training)
            setResearchMatches(research)
            setNavigatorScore(assessNavigatorFit())
            setShowResults(true)
            setIsSearching(false)
        }, 500)
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
                    <Target className="h-8 w-8 text-green-700" />
                    IHEP Opportunity Matching Engine
                </h1>
                <p className="text-gray-600 mt-2">
                    Discover personalized opportunities tailored to your skills and goals
                </p>
            </div>

                <Card className="mb-8">
                    <CardHeader>
                        <CardTitle>Participant Profile</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">Participant Name</Label>
                                <Input
                                    id="name"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Enter participant name"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="location">Location</Label>
                                <Input
                                    id="location"
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                    placeholder="e.g., Miami, FL"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label>Skills</Label>
                            <div className="flex gap-2">
                                <Input
                                    value={skillInput}
                                    onChange={(e) => setSkillInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                                    placeholder="Add a skill (e.g., Customer Service)"
                                />
                                <Button onClick={addSkill}>Add</Button>
                            </div>
                            <div className="flex flex-wrap gap-2 min-h-[40px]">
                                {skills.length === 0 ? (
                                    <p className="text-sm text-muted-foreground">No skills added yet</p>
                                ) : (
                                    skills.map((skill) => (
                                        <Badge key={skill} variant="default" className="flex items-center gap-1">
                                            {skill}
                                            <button onClick={() => removeSkill(skill)} className="ml-1">
                                                <X className="h-3 w-3" />
                                            </button>
                                        </Badge>
                                    ))
                                )}
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="availability">Availability</Label>
                                <Select value={availability} onValueChange={setAvailability}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="full-time">Full-time (40+ hrs/week)</SelectItem>
                                        <SelectItem value="part-time">Part-time (20-40 hrs/week)</SelectItem>
                                        <SelectItem value="flexible">Flexible (10-20 hrs/week)</SelectItem>
                                        <SelectItem value="weekend">Weekends only</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="experience">Experience Level</Label>
                                <Select value={experience} onValueChange={setExperience}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="entry">Entry Level (0-2 years)</SelectItem>
                                        <SelectItem value="intermediate">Intermediate (2-5 years)</SelectItem>
                                        <SelectItem value="experienced">Experienced (5+ years)</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="interests">Career Interests</Label>
                            <Textarea
                                id="interests"
                                value={interests}
                                onChange={(e) => setInterests(e.target.value)}
                                placeholder="Describe career goals, preferred industries, or work preferences..."
                                rows={4}
                            />
                        </div>

                        {error && (
                            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                                {error}
                            </div>
                        )}

                        <Button
                            onClick={handleFindOpportunities}
                            className="w-full gradient-primary"
                            size="lg"
                            disabled={isSearching}
                        >
                            {isSearching ? (
                                <>
                                    <span className="animate-spin mr-2">&#9696;</span>
                                    Searching...
                                </>
                            ) : (
                                'Find Opportunities'
                            )}
                        </Button>
                    </CardContent>
                </Card>

                {showResults && (
                    <div className="space-y-6">
                        {/* Gig Opportunities */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Briefcase className="h-5 w-5" />
                                    Immediate Gig Opportunities
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {gigMatches.map((opp, idx) => (
                                    <div key={idx} className="border rounded-lg p-4 hover:bg-accent transition-colors">
                                        <h3 className="font-semibold text-lg mb-2">{opp.title}</h3>
                                        <p className="text-sm text-muted-foreground mb-2">
                                            <strong>{opp.company}</strong> • {opp.pay} • {opp.hours}
                                            <br />{opp.location} • {opp.urgency}
                                        </p>
                                        <div className="flex flex-wrap gap-2 items-center">
                                            <Badge variant="secondary">{opp.matchScore}% Match</Badge>
                                            {opp.skills?.map((skill) => (
                                                <Badge key={skill} variant="outline">{skill}</Badge>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>

                        {/* Training Programs */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <GraduationCap className="h-5 w-5" />
                                    Career Development Programs
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {trainingMatches.map((prog, idx) => (
                                    <div key={idx} className="border rounded-lg p-4 hover:bg-accent transition-colors">
                                        <h3 className="font-semibold text-lg mb-2">{prog.title}</h3>
                                        <p className="text-sm text-muted-foreground">
                                            <strong>{prog.provider}</strong>
                                            <br />Duration: {prog.duration} • {prog.commitment}
                                            <br />Cost: {prog.cost}
                                            <br />Outcome: {prog.outcome}
                                        </p>
                                        <div className="mt-2">
                                            <Badge variant="secondary">{prog.matchScore}% Match</Badge>
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>

                        {/* Research Studies */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <FlaskConical className="h-5 w-5" />
                                    Research Study Opportunities
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {researchMatches.map((study, idx) => (
                                    <div key={idx} className="border rounded-lg p-4 hover:bg-accent transition-colors">
                                        <h3 className="font-semibold text-lg mb-2">{study.title}</h3>
                                        <p className="text-sm text-muted-foreground">
                                            <strong>{study.institution}</strong>
                                            <br />Compensation: {study.compensation}
                                            <br />Time: {study.commitment}
                                            <br />Eligibility: {study.criteria}
                                            <br /><em>{study.description}</em>
                                        </p>
                                        <div className="mt-2">
                                            <Badge variant="secondary">{study.matchScore}% Match</Badge>
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>

                        {/* Peer Navigator Track */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Users className="h-5 w-5" />
                                    Peer Navigator Track
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="border rounded-lg p-4 bg-primary/5">
                                    <h3 className="font-semibold text-lg mb-2">Peer Navigator Assessment</h3>
                                    <p className="text-sm mb-4">
                                        {navigatorScore >= 80
                                            ? 'Excellent fit! You have strong potential as a peer navigator.'
                                            : navigatorScore >= 70
                                                ? 'Good fit! Consider exploring the peer navigator pathway.'
                                                : 'Emerging potential. Navigator role may be a future option.'}
                                    </p>
                                    <p className="text-sm mb-4">
                                        <strong>Development Pathway:</strong><br />
                                        {navigatorScore >= 80
                                            ? 'Recommended: Enroll in Certified Peer Specialist Training immediately. Your profile shows natural alignment with navigator competencies.'
                                            : navigatorScore >= 70
                                                ? 'Recommended: Start with Healthcare Navigation Certificate to build foundational skills, then progress to full certification.'
                                                : 'Recommended: Focus on building communication and healthcare knowledge through Community Health Worker Training first.'}
                                    </p>
                                    <p className="text-sm mb-4">
                                        <strong>Why Become a Navigator?</strong><br />
                                        • Earn $22-32/hour with certification<br />
                                        • Make meaningful impact in your community<br />
                                        • Career advancement opportunities<br />
                                        • Leverage lived experience professionally
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        <Badge variant="secondary">{navigatorScore}% Navigator Fit</Badge>
                                        <Badge variant="outline">Career Growth</Badge>
                                        <Badge variant="outline">Community Impact</Badge>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                )}
        </div>
    )
}
