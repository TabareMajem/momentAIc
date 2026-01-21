
import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Lock, FileText, Share2, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function PrivacyPolicy() {
    return (
        <div className="min-h-screen bg-[#050505] text-gray-300">
            {/* Header */}
            <header className="fixed top-0 w-full z-50 border-b border-white/10 bg-[#050505]/80 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded bg-gradient-to-br from-[#00f0ff] to-[#0047ff] flex items-center justify-center font-bold text-black text-xl">M</div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                            MomentAIc
                        </span>
                    </Link>
                </div>
            </header>

            <main className="pt-24 pb-20 px-6 max-w-4xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-12 text-center"
                >
                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">Privacy Policy</h1>
                    <p className="text-xl text-gray-400">Effective Date: January 1, 2026</p>
                </motion.div>

                <div className="space-y-12 bg-white/5 border border-white/10 rounded-2xl p-8 md:p-12 backdrop-blur-sm">

                    {/* Introduction */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <Shield className="w-6 h-6 text-[#00f0ff]" />
                            1. Introduction
                        </h2>
                        <p className="leading-relaxed">
                            Welcome to MomentAIc ("we," "our," or "us"). We are committed to protecting your personal information and your right to privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website and SaaS platform (the "Service").
                        </p>
                    </section>

                    {/* Information We Collect */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <FileText className="w-6 h-6 text-[#00f0ff]" />
                            2. Information We Collect
                        </h2>
                        <ul className="list-disc pl-6 space-y-3 mt-4 text-gray-300">
                            <li>
                                <strong className="text-white">Personal Information:</strong> Name, email address, password, and contact details provided during registration.
                            </li>
                            <li>
                                <strong className="text-white">Business Data:</strong> Startup ideas, strategies, metrics, and other business-related inputs you provide to the Service.
                            </li>
                            <li>
                                <strong className="text-white">Integration Data:</strong> Information from connected services (Google, GitHub, LinkedIn, etc.) when you authorize integration. This includes OAuth tokens and profile data needed to execute requested actions.
                            </li>
                            <li>
                                <strong className="text-white">Usage Data:</strong> Log data, device information, and analytics on how you interact with our Service.
                            </li>
                        </ul>
                    </section>

                    {/* How We Use Your Information */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <CheckCircle className="w-6 h-6 text-[#00f0ff]" />
                            3. How We Use Your Information
                        </h2>
                        <p className="mb-4">We use the collected information for the following purposes:</p>
                        <ul className="list-disc pl-6 space-y-3 text-gray-300">
                            <li>To provide, operate, and maintain our Service.</li>
                            <li>To improve, personalize, and expand our Service.</li>
                            <li>To process transactions and manage user accounts.</li>
                            <li>To communicate with you, including customer service, updates, and marketing (which you can opt-out of).</li>
                            <li>To execute automated tasks via our AI Agents upon your instruction (e.g., analyzing a repo, scheduling a post).</li>
                        </ul>
                    </section>

                    {/* Data Sharing */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <Share2 className="w-6 h-6 text-[#00f0ff]" />
                            4. Sharing of Information
                        </h2>
                        <p className="mb-4">We do not sell your personal information. We may share your information with:</p>
                        <ul className="list-disc pl-6 space-y-3 text-gray-300">
                            <li>
                                <strong className="text-white">Service Providers:</strong> Third-party vendors who perform services on our behalf (e.g., payment processing via Stripe, cloud hosting).
                            </li>
                            <li>
                                <strong className="text-white">Legal Requirements:</strong> If required by law or to protect our rights and safety.
                            </li>
                            <li>
                                <strong className="text-white">Business Transfers:</strong> In connection with a merger, sale, or acquisition of our business.
                            </li>
                        </ul>
                    </section>

                    {/* Security */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <Lock className="w-6 h-6 text-[#00f0ff]" />
                            5. Data Security
                        </h2>
                        <p>
                            We use administrative, technical, and physical security measures to help protect your personal information. While we strive to protect your personal information, no method of transmission over the Internet is 100% secure. We cannot guarantee its absolute security.
                        </p>
                    </section>

                    {/* Contact Us */}
                    <section className="pt-6 border-t border-white/10">
                        <h2 className="text-2xl font-bold text-white mb-4">Contact Us</h2>
                        <p>
                            If you have questions or comments about this policy, you may email us at: <a href="mailto:support@momentaic.com" className="text-[#00f0ff] hover:underline">support@momentaic.com</a>
                        </p>
                    </section>

                </div>
            </main>
        </div>
    );
}
