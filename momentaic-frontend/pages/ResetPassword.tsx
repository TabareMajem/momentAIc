import React from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/Card';
import { ArrowLeft, Key, CheckCircle, AlertTriangle } from 'lucide-react';
import { Logo } from '../components/ui/Logo';

export default function ResetPassword() {
    const { register, handleSubmit, watch, formState: { errors } } = useForm();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = React.useState(false);
    const [isSuccess, setIsSuccess] = React.useState(false);
    const [error, setError] = React.useState('');

    const token = searchParams.get('token');
    const password = watch('password');

    const onSubmit = async (data: any) => {
        if (!token) return;

        try {
            setIsLoading(true);
            setError('');
            await api.resetPassword(token, data.password);
            setIsSuccess(true);
            setTimeout(() => navigate('/login'), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to reset password. The link may have expired.');
        } finally {
            setIsLoading(false);
        }
    };

    if (!token) {
        return (
            <div className="min-h-screen bg-[#020202] flex items-center justify-center p-4 relative overflow-hidden">
                <div className="absolute inset-0 bg-cyber-grid bg-[length:50px_50px] opacity-10 pointer-events-none"></div>

                <Card className="w-full max-w-md border-white/10 bg-[#050505]/80 backdrop-blur-xl">
                    <CardContent className="pt-8 pb-8 text-center space-y-4">
                        <div className="mx-auto w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center border border-red-500/20">
                            <AlertTriangle className="w-8 h-8 text-red-500" />
                        </div>
                        <h3 className="text-lg font-bold text-white">Invalid Reset Link</h3>
                        <p className="text-sm text-gray-400 font-mono">
                            This password reset link is invalid or missing. Please request a new one.
                        </p>
                        <Link to="/forgot-password">
                            <Button variant="cyber" className="mt-4">
                                Request New Link
                            </Button>
                        </Link>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#020202] flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 bg-cyber-grid bg-[length:50px_50px] opacity-10 pointer-events-none"></div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#00f0ff] opacity-[0.03] blur-[100px] rounded-full pointer-events-none"></div>

            <Link to="/login" className="absolute top-8 left-8 text-gray-500 hover:text-white flex items-center gap-2 font-mono text-sm tracking-widest transition-colors z-20">
                <ArrowLeft className="w-4 h-4" /> BACK TO LOGIN
            </Link>

            <div className="w-full max-w-md relative z-10 animate-fade-in-up">
                <div className="flex justify-center mb-8">
                    <Logo collapsed={false} />
                </div>

                <Card className="border-white/10 bg-[#050505]/80 backdrop-blur-xl shadow-[0_0_50px_rgba(0,0,0,0.5)]">
                    <CardHeader className="text-center pb-8 border-b border-white/5">
                        <div className="mx-auto w-12 h-12 bg-[#00f0ff]/10 rounded-full flex items-center justify-center mb-4 border border-[#00f0ff]/20 shadow-[0_0_15px_rgba(0,240,255,0.2)]">
                            <Key className="w-6 h-6 text-[#00f0ff]" />
                        </div>
                        <CardTitle className="text-2xl tracking-tighter">Reset Access Key</CardTitle>
                        <CardDescription>Enter your new password below</CardDescription>
                    </CardHeader>

                    {isSuccess ? (
                        <CardContent className="pt-8 pb-8 text-center space-y-4">
                            <div className="mx-auto w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center border border-green-500/20">
                                <CheckCircle className="w-8 h-8 text-green-500" />
                            </div>
                            <h3 className="text-lg font-bold text-white">Password Reset Complete</h3>
                            <p className="text-sm text-gray-400 font-mono">
                                Your password has been reset. Redirecting to login...
                            </p>
                        </CardContent>
                    ) : (
                        <form onSubmit={handleSubmit(onSubmit)}>
                            <CardContent className="space-y-4 pt-6">
                                {error && (
                                    <div className="p-3 text-xs text-red-400 bg-red-900/10 rounded border border-red-900/30 font-mono">
                                        ERROR: {error}
                                    </div>
                                )}
                                <Input
                                    label="New Password"
                                    type="password"
                                    placeholder="••••••••"
                                    {...register('password', {
                                        required: 'Password is required',
                                        minLength: { value: 8, message: 'Min 8 characters' },
                                        pattern: {
                                            value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                                            message: 'Must include uppercase, lowercase, and number'
                                        }
                                    })}
                                    error={errors.password?.message as string}
                                    className="bg-black border-white/10 focus:border-[#00f0ff]"
                                />
                                <Input
                                    label="Confirm Password"
                                    type="password"
                                    placeholder="••••••••"
                                    {...register('confirmPassword', {
                                        required: 'Please confirm your password',
                                        validate: value => value === password || "Passwords do not match"
                                    })}
                                    error={errors.confirmPassword?.message as string}
                                    className="bg-black border-white/10 focus:border-[#00f0ff]"
                                />
                            </CardContent>
                            <CardFooter className="flex flex-col space-y-4 pt-2 pb-8 bg-transparent border-t-0">
                                <Button
                                    type="submit"
                                    variant="cyber"
                                    className="w-full h-12 text-sm shadow-[0_0_20px_rgba(0,240,255,0.2)]"
                                    isLoading={isLoading}
                                >
                                    RESET PASSWORD
                                </Button>
                            </CardFooter>
                        </form>
                    )}
                </Card>
            </div>
        </div>
    );
}
