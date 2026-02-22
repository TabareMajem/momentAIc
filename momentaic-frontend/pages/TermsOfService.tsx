
import React from 'react';
import { Shield, FileText, CheckCircle, AlertTriangle, Scale } from 'lucide-react';
import { Link } from 'react-router-dom';

// Generated Asset
import policyHeaderImg from '/root/.gemini/antigravity/brain/ffd40e2c-57b3-4cfd-8eb2-314e12ced473/policy_shield_header_1770142403906.png';

export default function TermsOfService() {
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
                <div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-12 text-center"
                >
                    <div className="flex justify-center mb-6">
                        <div className="relative w-24 h-24 rounded-full overflow-hidden border border-[#00f0ff]/30 shadow-[0_0_30px_rgba(0,240,255,0.2)]">
                            <img src={policyHeaderImg} alt="Security Shield" className="w-full h-full object-cover" />
                        </div>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">Terms of Service</h1>
                    <p className="text-xl text-gray-400">Effective Date: January 1, 2026</p>
                </div>

                <div className="space-y-12 bg-white/5 border border-white/10 rounded-2xl p-8 md:p-12 backdrop-blur-sm">

                    {/* Agreement to Terms */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <FileText className="w-6 h-6 text-[#00f0ff]" />
                            1. Agreement to Terms
                        </h2>
                        <p className="leading-relaxed">
                            By accessing or using MomentAIc (the "Service"), you agree to be bound by these Terms of Service. If you disagree with any part of the terms, you may not access the Service.
                        </p>
                    </section>

                    {/* Use License */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <CheckCircle className="w-6 h-6 text-[#00f0ff]" />
                            2. Use License
                        </h2>
                        <p className="mb-4">Permission is granted to temporarily access the materials (information or software) on MomentAIc's website for personal, non-commercial transitory viewing only.</p>
                        <p>This license shall automatically terminate if you violate any of these restrictions and may be terminated by MomentAIc at any time.</p>
                    </section>

                    {/* AI Generated Content */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <Scale className="w-6 h-6 text-[#00f0ff]" />
                            3. AI Generated Content
                        </h2>
                        <p className="mb-4">
                            You acknowledge that the Service utilizes Artificial Intelligence to generate content, code, and strategies ("Generated Output").
                        </p>
                        <ul className="list-disc pl-6 space-y-3 text-gray-300">
                            <li>You own the rights to the Generated Output created for your account.</li>
                            <li>MomentAIc is not liable for any errors, hallucinations, or copyright infringements in the Generated Output.</li>
                            <li>You represent that you have the right to use any inputs provided to the AI.</li>
                        </ul>
                    </section>

                    {/* Disclaimer */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <AlertTriangle className="w-6 h-6 text-[#00f0ff]" />
                            4. Disclaimer
                        </h2>
                        <p>
                            The materials on MomentAIc's website are provided on an 'as is' basis. MomentAIc makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.
                        </p>
                    </section>

                    {/* Limitations */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                            <Shield className="w-6 h-6 text-[#00f0ff]" />
                            5. Limitations
                        </h2>
                        <p>
                            In no event shall MomentAIc or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on MomentAIc's website.
                        </p>
                    </section>

                    {/* Contact Us */}
                    <section className="pt-6 border-t border-white/10">
                        <h2 className="text-2xl font-bold text-white mb-4">Contact Us</h2>
                        <p>
                            If you have questions about these Terms, please contact us at: <a href="mailto:legal@momentaic.com" className="text-[#00f0ff] hover:underline">legal@momentaic.com</a>
                        </p>
                    </section>

                </div>
            </main>
        </div>
    );
}
