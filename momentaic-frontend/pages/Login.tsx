import React from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/auth-store';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/Card';
import { Bot, ArrowLeft, ShieldCheck } from 'lucide-react';
import { Logo } from '../components/ui/Logo';

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const { login, isLoading } = useAuthStore();
  const navigate = useNavigate();
  const [error, setError] = React.useState('');

  const onSubmit = async (data: any) => {
    try {
      setError('');
      await login(data.email, data.password);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-[#020202] flex items-center justify-center p-4 relative overflow-hidden">
       {/* Background Grid */}
       <div className="absolute inset-0 bg-cyber-grid bg-[length:50px_50px] opacity-10 pointer-events-none"></div>
       <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#2563eb] opacity-[0.03] blur-[100px] rounded-full pointer-events-none"></div>

       <Link to="/" className="absolute top-8 left-8 text-gray-500 hover:text-white flex items-center gap-2 font-mono text-sm tracking-widest transition-colors z-20">
         <ArrowLeft className="w-4 h-4" /> ABORT
       </Link>

      <div className="w-full max-w-md relative z-10 animate-fade-in-up">
        <div className="flex justify-center mb-8">
            <Logo collapsed={false} />
        </div>

        <Card className="border-white/10 bg-[#050505]/80 backdrop-blur-xl shadow-[0_0_50px_rgba(0,0,0,0.5)]">
          <CardHeader className="text-center pb-8 border-b border-white/5">
            <div className="mx-auto w-12 h-12 bg-[#2563eb]/10 rounded-full flex items-center justify-center mb-4 border border-[#2563eb]/20 shadow-[0_0_15px_rgba(37,99,235,0.2)]">
               <ShieldCheck className="w-6 h-6 text-[#2563eb]" />
            </div>
            <CardTitle className="text-2xl tracking-tighter">Identity Verification</CardTitle>
            <CardDescription>Enter credentials to access Mission Control</CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <CardContent className="space-y-6 pt-6">
              {error && (
                <div className="p-3 text-xs text-red-400 bg-red-900/10 rounded border border-red-900/30 font-mono">
                  ERROR: {error}
                </div>
              )}
              <Input
                label="Authorized Email"
                type="email"
                placeholder="founder@entity.com"
                {...register('email', { required: 'Email is required' })}
                error={errors.email?.message as string}
                className="bg-black border-white/10 focus:border-[#2563eb]"
              />
              <div className="space-y-1">
                  <Input
                    label="Access Key (Password)"
                    type="password"
                    placeholder="••••••••"
                    {...register('password', { required: 'Password is required' })}
                    error={errors.password?.message as string}
                    className="bg-black border-white/10 focus:border-[#2563eb]"
                  />
                  <div className="flex justify-end">
                      <a href="#" className="text-[10px] text-gray-500 hover:text-[#2563eb] font-mono transition-colors">FORGOT KEY?</a>
                  </div>
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4 pt-2 pb-8 bg-transparent border-t-0">
              <Button type="submit" variant="cyber" className="w-full h-12 text-sm shadow-[0_0_20px_rgba(37,99,235,0.2)]" isLoading={isLoading}>
                AUTHENTICATE
              </Button>
              <div className="text-center text-xs font-mono text-gray-600">
                NO ACCESS?{' '}
                <Link to="/signup" className="text-[#00f0ff] hover:text-white transition-colors">
                  REQUEST CLEARANCE
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}