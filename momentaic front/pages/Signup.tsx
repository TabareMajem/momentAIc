import React from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/auth-store';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/Card';
import { Bot, ArrowLeft, Cpu } from 'lucide-react';
import { Logo } from '../components/ui/Logo';

export default function SignupPage() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm();
  const { signup, isLoading } = useAuthStore();
  const navigate = useNavigate();
  const [error, setError] = React.useState('');

  const password = watch('password');

  const onSubmit = async (data: any) => {
    try {
      setError('');
      await signup(data.email, data.password, data.fullName);
      navigate('/dashboard');
    } catch (err: any) {
      // Parse validation errors from backend
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail) && detail.length > 0) {
        // Pydantic validation errors
        const messages = detail.map((e: any) => e.msg || e.message).filter(Boolean);
        setError(messages.join('. ') || 'Validation failed.');
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError(err.response?.data?.message || err.response?.data?.error || 'Initialization failed. Please try again.');
      }
    }
  };


  return (
    <div className="min-h-screen bg-[#020202] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-cyber-grid bg-[length:50px_50px] opacity-10 pointer-events-none"></div>
      <div className="absolute bottom-0 right-0 w-[800px] h-[800px] bg-[#00f0ff] opacity-[0.03] blur-[100px] rounded-full pointer-events-none"></div>

      <Link to="/" className="absolute top-8 left-8 text-gray-500 hover:text-white flex items-center gap-2 font-mono text-sm tracking-widest transition-colors z-20">
        <ArrowLeft className="w-4 h-4" /> BACK TO BASE
      </Link>

      <div className="w-full max-w-md relative z-10 animate-fade-in-up">
        <div className="flex justify-center mb-8">
          <Logo collapsed={false} />
        </div>

        <Card className="border-white/10 bg-[#050505]/80 backdrop-blur-xl shadow-[0_0_50px_rgba(0,0,0,0.5)]">
          <CardHeader className="text-center pb-8 border-b border-white/5">
            <div className="mx-auto w-12 h-12 bg-[#00f0ff]/10 rounded-full flex items-center justify-center mb-4 border border-[#00f0ff]/20 shadow-[0_0_15px_rgba(0,240,255,0.2)]">
              <Cpu className="w-6 h-6 text-[#00f0ff]" />
            </div>
            <CardTitle className="text-2xl tracking-tighter">Initialize Protocol</CardTitle>
            <CardDescription>Create your admin credentials to begin</CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <CardContent className="space-y-4 pt-6">
              {error && (
                <div className="p-3 text-xs text-red-400 bg-red-900/10 rounded border border-red-900/30 font-mono">
                  ERROR: {error}
                </div>
              )}
              <Input
                label="Operator Name"
                placeholder="Elon Musk"
                {...register('fullName', { required: 'Full name is required' })}
                error={errors.fullName?.message as string}
                className="bg-black border-white/10 focus:border-[#00f0ff]"
              />
              <Input
                label="Contact Email"
                type="email"
                placeholder="founder@mars.com"
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Invalid format"
                  }
                })}
                error={errors.email?.message as string}
                className="bg-black border-white/10 focus:border-[#00f0ff]"
              />
              <Input
                label="Secret Key"
                type="password"
                placeholder="••••••••"
                {...register('password', {
                  required: 'Password is required',
                  minLength: { value: 6, message: 'Min 6 chars' }
                })}
                error={errors.password?.message as string}
                className="bg-black border-white/10 focus:border-[#00f0ff]"
              />
              <Input
                label="Verify Key"
                type="password"
                placeholder="••••••••"
                {...register('confirmPassword', {
                  required: 'Confirmation required',
                  validate: value => value === password || "Keys do not match"
                })}
                error={errors.confirmPassword?.message as string}
                className="bg-black border-white/10 focus:border-[#00f0ff]"
              />
            </CardContent>
            <CardFooter className="flex flex-col space-y-4 pt-2 pb-8 bg-transparent border-t-0">
              <Button type="submit" variant="cyber" className="w-full h-12 text-sm shadow-[0_0_20px_rgba(0,240,255,0.2)] border-[#00f0ff] text-black bg-[#00f0ff] hover:bg-white hover:text-black hover:border-white" isLoading={isLoading}>
                ESTABLISH UPLINK
              </Button>
              <div className="text-center text-xs font-mono text-gray-600">
                ALREADY OPERATIONAL?{' '}
                <Link to="/login" className="text-[#2563eb] hover:text-white transition-colors">
                  LOGIN HERE
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}