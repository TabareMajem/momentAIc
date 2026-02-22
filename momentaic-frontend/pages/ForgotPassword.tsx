import React from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/Card';
import { ArrowLeft, Mail, CheckCircle } from 'lucide-react';
import { Logo } from '../components/ui/Logo';

export default function ForgotPassword() {
    const { register, handleSubmit, formState: { errors } } = useForm();
    const [isLoading, setIsLoading] = React.useState(false);
    const [isSuccess, setIsSuccess] = React.useState(false);
    const [error, setError] = React.useState('');

    const onSubmit = async (data: any) => {
        try {
            setIsLoading(true);
            setError('');
            await api.forgotPassword(data.email);
            setIsSuccess(true);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to send reset email. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#020202] flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 bg-cyber-grid bg-[length:50px_50px] opacity-10 pointer-events-none"></div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#a855f7] opacity-[0.03] blur-[100px] rounded-full pointer-events-none"></div>

            <Link to="/login" className="absolute top-8 left-8 text-gray-500 hover:text-white flex items-center gap-2 font-mono text-sm tracking-widest transition-colors z-20">
                <ArrowLeft className="w-4 h-4" /> BACK TO LOGIN
            </Link>

            <div className="w-full max-w-md relative z-10 animate-fade-in-up">
                <div className="flex justify-center mb-8">
                    <Logo collapsed={false} />
                </div>

                <Card className="border-white/10 bg-[#050505]/80 backdrop-blur-xl shadow-[0_0_50px_rgba(0,0,0,0.5)]">
                    <CardHeader className="text-center pb-8 border-b border-white/5">
                        <div className="mx-auto w-12 h-12 bg-[#a855f7]/10 rounded-full flex items-center justify-center mb-4 border border-[#a855f7]/20 shadow-[0_0_15px_rgba(168,85,247,0.2)]">
                            <Mail className="w-6 h-6 text-[#a855f7]" />
                        </div>
                        <CardTitle className="text-2xl tracking-tighter">Key Recovery</CardTitle>
                        <CardDescription>Enter your email to receive a password reset link</CardDescription>
                    </CardHeader>

                    {isSuccess ? (
                        <CardContent className="pt-8 pb-8 text-center space-y-4">
                            <div className="mx-auto w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center border border-green-500/20">
                                <CheckCircle className="w-8 h-8 text-green-500" />
                            </div>
                            <h3 className="text-lg font-bold text-white">Recovery Link Sent</h3>
                            <p className="text-sm text-gray-400 font-mono">
                                If an account with that email exists, you'll receive a password reset link shortly.
                            </p>
                            <Link to="/login">
                                <Button variant="outline" className="mt-4 border-white/10">
                                    Return to Login
                                </Button>
                            </Link>
                        </CardContent>
                    ) : (
                        <form onSubmit={handleSubmit(onSubmit)}>
                            <CardContent className="space-y-6 pt-6">
                                {error && (
                                    <div className="p-3 text-xs text-red-400 bg-red-900/10 rounded border border-red-900/30 font-mono">
                                        ERROR: {error}
                                    </div>
                                )}
                                <Input
                                    label="Registered Email"
                                    type="email"
                                    placeholder="founder@entity.com"
                                    {...register('email', { required: 'Email is required' })}
                                    error={errors.email?.message as string}
                                    className="bg-black border-white/10 focus:border-[#a855f7]"
                                />
                            </CardContent>
                            <CardFooter className="flex flex-col space-y-4 pt-2 pb-8 bg-transparent border-t-0">
                                <Button
                                    type="submit"
                                    variant="cyber"
                                    className="w-full h-12 text-sm shadow-[0_0_20px_rgba(168,85,247,0.2)] border-[#a855f7] text-[#a855f7] hover:bg-[#a855f7] hover:text-black"
                                    isLoading={isLoading}
                                >
                                    SEND RECOVERY LINK
                                </Button>
                                <div className="text-center text-xs font-mono text-gray-600">
                                    REMEMBER YOUR KEY?{' '}
                                    <Link to="/login" className="text-[#2563eb] hover:text-white transition-colors">
                                        LOGIN HERE
                                    </Link>
                                </div>
                            </CardFooter>
                        </form>
                    )}
                </Card>
            </div>
        </div>
    );
}
