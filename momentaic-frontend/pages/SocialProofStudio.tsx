import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { useToast } from '../components/ui/Toast';
import { useAuthStore } from '../stores/auth-store';
import { cn } from '../lib/utils';
import {
    MessageSquare, FileText, Award, Star, Copy, Download,
    Sparkles, CheckCircle, ExternalLink, Users, Building2,
    Quote, Camera, Video, Zap, ChevronRight, RefreshCw
} from 'lucide-react';

// ============ TYPES ============

interface TestimonialRequest {
    customer_name: string;
    company: string;
    role: string;
    use_case: string;
    result: string;
}

interface GeneratedTestimonial {
    short: string;
    medium: string;
    long: string;
    tweet: string;
    linkedin: string;
}

interface CaseStudySection {
    challenge: string;
    solution: string;
    results: string;
    quote: string;
}

// ============ TEMPLATE DATA ============

const TESTIMONIAL_TEMPLATES = [
    {
        id: 'saas',
        name: 'SaaS Product',
        icon: '💻',
        template: "Before [Product], we spent hours on [pain point]. Now we [benefit] in minutes. It's been a game-changer for our team.",
    },
    {
        id: 'productivity',
        name: 'Productivity Tool',
        icon: '⚡',
        template: "[Product] saved me [X hours] per week. I can't imagine going back to the old way of doing things.",
    },
    {
        id: 'agency',
        name: 'Agency/Consultant',
        icon: '🏢',
        template: "Our clients love the results we deliver using [Product]. It's helped us [specific outcome] and grow our business by [metric].",
    },
    {
        id: 'startup',
        name: 'Startup Founder',
        icon: '🚀',
        template: "As a startup, every dollar counts. [Product] gave us [outcome] without the huge investment in [alternative].",
    },
];

const CASE_STUDY_SECTIONS = [
    { id: 'challenge', label: 'Challenge', icon: '🎯', placeholder: 'What problem were they facing?' },
    { id: 'solution', label: 'Solution', icon: '💡', placeholder: 'How did your product help?' },
    { id: 'results', label: 'Results', icon: '📈', placeholder: 'What metrics improved?' },
    { id: 'quote', label: 'Quote', icon: '💬', placeholder: 'Customer testimonial quote' },
];

const SOCIAL_PROOF_WIDGETS = [
    { id: 'customer_count', name: 'Customer Count', example: '1,000+ startups trust MomentAIc', icon: '👥' },
    { id: 'rating', name: 'Rating Badge', example: '⭐ 4.9/5 from 500+ reviews', icon: '⭐' },
    { id: 'featured', name: 'As Featured In', example: 'Featured in TechCrunch, Forbes', icon: '📰' },
    { id: 'backed_by', name: 'Backed By', example: 'Backed by Y Combinator', icon: '🏦' },
    { id: 'awards', name: 'Awards', example: 'Product of the Day on Product Hunt', icon: '🏆' },
];

// ============ TESTIMONIAL GENERATOR COMPONENT ============

function TestimonialGenerator() {
    const { user } = useAuthStore();
    const [formData, setFormData] = useState<TestimonialRequest>({
        customer_name: '',
        company: (user as any)?.company_name || '',
        role: '',
        use_case: '',
        result: '',
    });
    const [generated, setGenerated] = useState<GeneratedTestimonial | null>(null);
    const [generating, setGenerating] = useState(false);
    const { toast } = useToast();

    const generateTestimonials = async () => {
        if (!formData.customer_name || !formData.use_case) {
            toast({ type: 'error', title: 'Missing Info', message: 'Please fill in customer name and use case' });
            return;
        }

        setGenerating(true);
        await new Promise(r => setTimeout(r, 1500));

        const generated: GeneratedTestimonial = {
            short: `"${formData.result || 'Game-changer'}!" - ${formData.customer_name}, ${formData.role || 'Founder'}`,
            medium: `"MomentAIc helped us ${formData.use_case}. ${formData.result || 'We couldn\'t be happier with the results'}." - ${formData.customer_name}, ${formData.role || 'Founder'} at ${formData.company || 'Startup'}`,
            long: `"Before discovering MomentAIc, we struggled with ${formData.use_case}. Since implementing it, ${formData.result || 'we\'ve seen incredible improvements'}. The AI agents are like having a full team at your fingertips. I highly recommend it to any startup founder." - ${formData.customer_name}, ${formData.role || 'Founder'} at ${formData.company || 'their startup'}`,
            tweet: `🚀 Shoutout to @MomentAIc for helping us ${formData.use_case}!\n\n${formData.result || 'Absolute game-changer'} for our team.\n\n#StartupLife #AI #Productivity`,
            linkedin: `I wanted to share my experience with MomentAIc.\n\nAs ${formData.role || 'a founder'} at ${formData.company || 'my startup'}, I was looking for a way to ${formData.use_case}.\n\nThe results?\n✅ ${formData.result || 'Incredible time savings'}\n✅ Better decision-making\n✅ AI-powered insights\n\nHighly recommend checking it out if you're a startup founder!`,
        };

        setGenerated(generated);
        setGenerating(false);
    };

    const copyText = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        toast({ type: 'success', title: 'Copied!', message: `${label} copied to clipboard` });
    };

    return (
        <div className="space-y-6">
            {/* Input Form */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                    label="Customer Name"
                    placeholder="e.g., Sarah Chen"
                    value={formData.customer_name}
                    onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                />
                <Input
                    label="Company"
                    placeholder="e.g., TechStartup Inc."
                    value={formData.company}
                    onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                />
                <Input
                    label="Role/Title"
                    placeholder="e.g., CEO & Founder"
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                />
                <Input
                    label="Key Result"
                    placeholder="e.g., Saved 20 hours per week"
                    value={formData.result}
                    onChange={(e) => setFormData({ ...formData, result: e.target.value })}
                />
            </div>
            <Textarea
                label="Use Case / What They Achieved"
                placeholder="e.g., automate our marketing workflows and track growth metrics"
                value={formData.use_case}
                onChange={(e) => setFormData({ ...formData, use_case: e.target.value })}
                className="h-20"
            />

            <Button onClick={generateTestimonials} isLoading={generating} variant="cyber" className="w-full">
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Testimonials
            </Button>

            {/* Generated Testimonials */}
            {generated && (
                <div className="space-y-4 mt-6">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Quote className="w-5 h-5 text-[#00f0ff]" />
                        Generated Testimonials
                    </h3>

                    {[
                        { label: 'Short (Website)', value: generated.short },
                        { label: 'Medium (Landing Page)', value: generated.medium },
                        { label: 'Long (Case Study)', value: generated.long },
                        { label: 'Twitter Post', value: generated.tweet },
                        { label: 'LinkedIn Post', value: generated.linkedin },
                    ].map((item) => (
                        <Card key={item.label} className="p-4 bg-black/50 border-white/10">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs text-gray-400 uppercase tracking-wider">{item.label}</span>
                                <Button size="sm" variant="ghost" onClick={() => copyText(item.value, item.label)}>
                                    <Copy className="w-3 h-3 mr-1" /> Copy
                                </Button>
                            </div>
                            <p className="text-sm text-gray-300 whitespace-pre-wrap">{item.value}</p>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}

// ============ CASE STUDY BUILDER COMPONENT ============

function CaseStudyBuilder() {
    const { user } = useAuthStore();
    const [sections, setSections] = useState({
        challenge: '',
        solution: '',
        results: '',
        quote: '',
    });
    // Auto-fill from user context if available
    const [companyName, setCompanyName] = useState((user as any)?.company_name || '');
    const [industry, setIndustry] = useState('');
    const { toast } = useToast();

    const generateCaseStudy = () => {
        const caseStudy = `
# Case Study: ${companyName || '[Company Name]'}
**Industry:** ${industry || 'Technology'}

## The Challenge
${sections.challenge || 'Describe the challenge here...'}

## The Solution
${sections.solution || 'Describe how your product helped...'}

## The Results
${sections.results || 'Share the measurable outcomes...'}

## What They Say
> "${sections.quote || 'Add a customer quote here...'}"
        `;
        navigator.clipboard.writeText(caseStudy);
        toast({ type: 'success', title: 'Copied!', message: 'Case study copied as Markdown' });
    };

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                    label="Company Name"
                    placeholder="e.g., Acme Corp"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                />
                <Input
                    label="Industry"
                    placeholder="e.g., SaaS, E-commerce"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                />
            </div>

            {CASE_STUDY_SECTIONS.map((section) => (
                <div key={section.id}>
                    <label className="flex items-center gap-2 text-sm font-medium text-gray-400 mb-2">
                        <span>{section.icon}</span>
                        {section.label}
                    </label>
                    <Textarea
                        placeholder={section.placeholder}
                        value={sections[section.id as keyof typeof sections]}
                        onChange={(e) => setSections({ ...sections, [section.id]: e.target.value })}
                        className="h-24"
                    />
                </div>
            ))}

            <div className="flex gap-3">
                <Button onClick={generateCaseStudy} variant="cyber" className="flex-1">
                    <Download className="w-4 h-4 mr-2" />
                    Export as Markdown
                </Button>
            </div>
        </div>
    );
}

// ============ SOCIAL PROOF WIDGET BUILDER ============

function WidgetBuilder() {
    const [selectedWidget, setSelectedWidget] = useState(SOCIAL_PROOF_WIDGETS[0]);
    const [customText, setCustomText] = useState(SOCIAL_PROOF_WIDGETS[0].example);
    const { toast } = useToast();

    const copyWidget = () => {
        const html = `<div class="social-proof-widget">${customText}</div>`;
        navigator.clipboard.writeText(html);
        toast({ type: 'success', title: 'Copied!', message: 'Widget HTML copied' });
    };

    return (
        <div className="space-y-6">
            {/* Widget Type Selector */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {SOCIAL_PROOF_WIDGETS.map((widget) => (
                    <button
                        key={widget.id}
                        onClick={() => {
                            setSelectedWidget(widget);
                            setCustomText(widget.example);
                        }}
                        className={cn(
                            "p-3 rounded-lg border text-center transition-all",
                            selectedWidget.id === widget.id
                                ? "border-[#00f0ff] bg-[#00f0ff]/10"
                                : "border-white/10 bg-black/50 hover:border-white/30"
                        )}
                    >
                        <span className="text-2xl block mb-1">{widget.icon}</span>
                        <span className="text-xs text-gray-400">{widget.name}</span>
                    </button>
                ))}
            </div>

            {/* Widget Preview */}
            <Card className="p-6 bg-gradient-to-br from-[#00f0ff]/5 to-transparent border-[#00f0ff]/20">
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-3">Preview</div>
                <div className="bg-black/50 p-4 rounded-lg border border-white/10">
                    <Input
                        value={customText}
                        onChange={(e) => setCustomText(e.target.value)}
                        className="text-lg font-bold text-center bg-transparent border-none text-white"
                    />
                </div>
                <Button onClick={copyWidget} variant="outline" className="w-full mt-4">
                    <Copy className="w-4 h-4 mr-2" />
                    Copy Widget Code
                </Button>
            </Card>
        </div>
    );
}

// ============ TESTIMONIAL REQUEST TEMPLATES ============

function RequestTemplates() {
    const { toast } = useToast();

    const templates = [
        {
            name: 'Quick Ask',
            subject: 'Quick favor?',
            body: `Hey [Name],\n\nHope you're doing well! Quick question - would you be open to sharing a short testimonial about your experience with [Product]?\n\nIt would really help other founders make their decision.\n\nNo pressure at all! Just a sentence or two would be amazing.\n\nThanks!\n[Your Name]`,
        },
        {
            name: 'Case Study Request',
            subject: 'Would love to feature you!',
            body: `Hi [Name],\n\nI've been so impressed with how you've been using [Product] - your results are incredible!\n\nWould you be open to being featured as a case study on our website? It would involve:\n\n• A 15-minute call to discuss your experience\n• We'll write everything up for you\n• You get final approval before publishing\n\nWe'd also love to promote your company to our audience.\n\nLet me know if you're interested!\n\nBest,\n[Your Name]`,
        },
        {
            name: 'Video Review',
            subject: 'Quick video testimonial?',
            body: `Hey [Name],\n\nYour success with [Product] has been amazing! Would you be willing to record a quick 60-second video testimonial?\n\nIt can be super casual - just you talking about:\n• What problem you were facing\n• How [Product] helped\n• Your results\n\nWe can even send you some talking points if helpful!\n\nAs a thank you, we'd love to offer you [incentive].\n\nInterested?\n\n[Your Name]`,
        },
    ];

    const copyTemplate = (template: typeof templates[0]) => {
        navigator.clipboard.writeText(`Subject: ${template.subject}\n\n${template.body}`);
        toast({ type: 'success', title: 'Copied!', message: `${template.name} template copied` });
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {templates.map((template) => (
                <Card key={template.name} className="p-4 bg-black/50 border-white/10 flex flex-col">
                    <div className="flex-1">
                        <h4 className="font-bold text-white mb-2">{template.name}</h4>
                        <p className="text-xs text-gray-500 mb-3">Subject: {template.subject}</p>
                        <p className="text-xs text-gray-400 line-clamp-4">{template.body}</p>
                    </div>
                    <Button
                        onClick={() => copyTemplate(template)}
                        variant="outline"
                        size="sm"
                        className="mt-4 w-full"
                    >
                        <Copy className="w-3 h-3 mr-2" />
                        Copy Template
                    </Button>
                </Card>
            ))}
        </div>
    );
}

// ============ MAIN COMPONENT ============

export default function SocialProofStudio() {
    const [activeTab, setActiveTab] = useState<'testimonials' | 'casestudy' | 'widgets' | 'requests'>('testimonials');

    const tabs = [
        { id: 'testimonials', label: 'Testimonial Generator', icon: Quote },
        { id: 'casestudy', label: 'Case Study Builder', icon: FileText },
        { id: 'widgets', label: 'Social Proof Widgets', icon: Award },
        { id: 'requests', label: 'Request Templates', icon: MessageSquare },
    ];

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="border-b border-white/10 pb-6">
                <h1 className="text-3xl font-black text-white tracking-tighter flex items-center gap-3">
                    <Award className="w-8 h-8 text-[#00f0ff]" />
                    SOCIAL_PROOF_STUDIO
                    <Badge variant="cyber" className="text-xs">BUILD CREDIBILITY</Badge>
                </h1>
                <p className="text-gray-500 font-mono text-sm mt-2">
                    Generate testimonials, case studies, and social proof that converts.
                </p>
            </div>

            {/* Tab Navigation */}
            <div className="flex flex-wrap gap-2">
                {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={cn(
                                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all",
                                activeTab === tab.id
                                    ? "bg-[#00f0ff] text-black"
                                    : "bg-black/50 text-gray-400 border border-white/10 hover:border-white/30"
                            )}
                        >
                            <Icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            {/* Tab Content */}
            <Card className="p-6 bg-black/30 border-white/10">
                {activeTab === 'testimonials' && <TestimonialGenerator />}
                {activeTab === 'casestudy' && <CaseStudyBuilder />}
                {activeTab === 'widgets' && <WidgetBuilder />}
                {activeTab === 'requests' && <RequestTemplates />}
            </Card>
        </div>
    );
}
