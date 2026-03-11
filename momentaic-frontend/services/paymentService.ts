
import { BackendService } from './backendService';

// Stripe Publishable Key - loaded from environment
// @ts-ignore - Vite provides import.meta.env at runtime
const STRIPE_KEY = (import.meta as any).env?.VITE_STRIPE_PUBLISHABLE_KEY || '';

export interface CreditPack {
    id: string;
    amount: number;
    price: number;
    label: string;
    popular?: boolean;
}

export interface SubscriptionPlan {
    id: string;
    name: string;
    price: string;
    period: string;
    tier: 'STARTER' | 'PRO' | 'ENTERPRISE';
    description: string;
    features: string[];
    popular?: boolean;
    buttonText: string;
    creditLimit: number;
}

export const CREDIT_PACKS: CreditPack[] = [
    { id: 'price_starter_pack', amount: 10000, price: 10.00, label: "Starter Pack" },
    { id: 'price_pro_pack', amount: 55000, price: 50.00, label: "Creator Pack", popular: true },
    { id: 'price_agency_pack', amount: 250000, price: 200.00, label: "Agency Pack" }
];

export const SUBSCRIPTION_PLANS: SubscriptionPlan[] = [
    {
        id: 'sub_starter',
        name: 'Starter',
        price: '$9',
        period: '/mo',
        tier: 'STARTER',
        description: 'Perfect for solo founders utilizing Gemini Flash.',
        buttonText: 'Start Building',
        creditLimit: 25000, // ~1000+ Flash queries
        features: [
            '25,000 Monthly Credits',
            'Gemini 2.5 Flash Access',
            'Standard Speed',
            '3 Active Agents'
        ]
    },
    {
        id: 'sub_pro',
        name: 'Pro',
        price: '$29',
        period: '/mo',
        tier: 'PRO',
        popular: true,
        description: 'For power users needing Veo Video & Gemini 3 Pro.',
        buttonText: 'Go Pro',
        creditLimit: 100000, // Margin protection: Veo videos cost ~2000 credits each
        features: [
            '100,000 Monthly Credits',
            'Gemini 3 Pro & Veo Access',
            'Hybrid Mode (BYO Key) Enabled',
            'Viral Strategy Engine',
            'Priority Support'
        ]
    },
    {
        id: 'sub_enterprise',
        name: 'Enterprise',
        price: 'Contact',
        period: '',
        tier: 'ENTERPRISE',
        description: 'For organizations scaling with custom needs.',
        buttonText: 'Contact Sales',
        creditLimit: 1000000,
        features: [
            'Unlimited Credits (Custom Pricing)',
            'Custom Integrations',
            'Dedicated Account Manager',
            'SLA & SSO',
            'White Label Options'
        ]
    }
];

/**
 * Initiates the Stripe Checkout flow.
 * Calls the backend to create a Stripe checkout session,
 * then redirects the browser to the Stripe hosted checkout page.
 */
export const initiateCheckout = async (priceId: string, type: 'CREDIT' | 'SUBSCRIPTION' = 'CREDIT'): Promise<{ success: boolean; message?: string; url?: string }> => {
    console.log(`[Stripe] Initiating ${type} checkout for ${priceId}`);

    try {
        // Call backend to create Stripe checkout session
        const mode = type === 'SUBSCRIPTION' ? 'subscription' : 'payment';
        const response = await BackendService.createCheckoutSession(priceId, mode);

        if (response.url) {
            // Redirect to Stripe Checkout
            window.location.href = response.url;
            return { success: true, message: "Redirecting to secure payment...", url: response.url };
        } else {
            return { success: false, message: response.error || "Failed to create checkout session" };
        }
    } catch (error: any) {
        console.error('[Stripe] Checkout error:', error);
        return { success: false, message: error.message || "Payment initialization failed" };
    }
};

/**
 * Get Stripe publishable key for frontend initialization
 */
export const getStripePublishableKey = (): string => {
    return STRIPE_KEY;
};
