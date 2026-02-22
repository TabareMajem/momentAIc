
import React from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/auth-store';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/Card';
import { Bot, ArrowLeft, Loader2 } from 'lucide-react';
import { Logo } from '../components/ui/Logo';
import { signInWithGoogle, signInWithGithub } from '../lib/firebase';

export default function SignupPage() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm();
  const { signup, firebaseLogin, isLoading } = useAuthStore();
  const navigate = useNavigate();
  const [error, setError] = React.useState('');

  const password = watch('password');

  const onSubmit = async (data: any) => {
    try {
      setError('');
      await signup(data.email, data.password, data.fullName);
      // Redirect to the new Genius Onboarding flow
      navigate('/onboarding/genius');
    } catch (err: any) {
      // Parse validation errors from backend
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail) && detail.length > 0) {
        const messages = detail.map((e: any) => e.msg || e.message).filter(Boolean);
        setError(messages.join('. ') || 'Validation failed.');
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError(err.response?.data?.message || err.response?.data?.error || 'Registration failed. Please try again.');
      }
    }
  };

  const handleGoogleSignup = async () => {
    try {
      setError('');
      const result = await signInWithGoogle();
      const idToken = await result.user.getIdToken();
      await firebaseLogin(idToken);
      navigate('/onboarding/genius');
    } catch (err: any) {
      console.error(err);
      if (err.code === 'auth/account-exists-with-different-credential') {
        setError('Account exists with a different sign-in method. Please use GitHub or log in with Email/Password.');
      } else {
        setError('Google auth failed.');
      }
    }
  };

  const handleGithubSignup = async () => {
    try {
      setError('');
      const result = await signInWithGithub();
      const idToken = await result.user.getIdToken();
      await firebaseLogin(idToken);
      navigate('/onboarding/genius');
    } catch (err: any) {
      console.error(err);
      if (err.code === 'auth/account-exists-with-different-credential') {
        setError('Account exists with a different sign-in method. Please use Google or log in with Email/Password.');
      } else {
        setError('GitHub auth failed.');
      }
    }
  };


  return (
    <div className="min-h-screen bg-[#050508] flex items-center justify-center p-4 relative overflow-hidden">

      {/* Ambient Background */}
      <div className="absolute top-[-10%] right-[-10%] w-[600px] h-[600px] bg-purple-600/5 blur-[100px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-cyan-600/5 blur-[100px] rounded-full pointer-events-none" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />

      <Link to="/" className="absolute top-8 left-8 text-gray-500 hover:text-white flex items-center gap-2 text-sm font-medium transition-colors z-20">
        <ArrowLeft className="w-4 h-4" /> Back to Home
      </Link>

      <div className="w-full max-w-md relative z-10 animate-fade-in-up">
        <div className="flex justify-center mb-6">
          <Logo collapsed={false} />
        </div>

        <Card className="border-white/5 bg-[#0a0a0f]/80 backdrop-blur-xl shadow-2xl">
          <CardHeader className="text-center pb-6 border-b border-white/5">
            <CardTitle className="text-2xl font-bold text-white">Create your account</CardTitle>
            <CardDescription className="text-gray-400">Start your 14-day free trial. No credit card required.</CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <CardContent className="space-y-4 pt-6">
              {error && (
                <div className="p-3 text-sm text-red-400 bg-red-500/10 rounded-lg border border-red-500/20">
                  {error}
                </div>
              )}
              <Input
                label="Full Name"
                placeholder="Elon Musk"
                {...register('fullName', { required: 'Full name is required' })}
                error={errors.fullName?.message as string}
                className="bg-black/50 border-white/10 focus:border-purple-500 rounded-lg"
              />
              <Input
                label="Work Email"
                type="email"
                placeholder="founder@company.com"
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Invalid email address"
                  }
                })}
                error={errors.email?.message as string}
                className="bg-black/50 border-white/10 focus:border-purple-500 rounded-lg"
              />
              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                {...register('password', {
                  required: 'Password is required',
                  minLength: { value: 6, message: 'Password must be at least 6 characters' }
                })}
                error={errors.password?.message as string}
                className="bg-black/50 border-white/10 focus:border-purple-500 rounded-lg"
              />

              <p className="text-xs text-center text-gray-500 mt-4">
                By clicking "Get Started", you agree to our <Link to="/terms" className="text-gray-400 hover:text-white underline">Terms</Link> and <Link to="/privacy" className="text-gray-400 hover:text-white underline">Privacy Policy</Link>.
              </p>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4 pt-2 pb-6 bg-transparent border-t-0">
              <Button
                type="submit"
                className="w-full h-11 text-base bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-medium rounded-xl shadow-lg shadow-purple-500/20 border-0"
                isLoading={isLoading}
              >
                Get Started
              </Button>

              <div className="relative my-2 w-full">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/10"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-transparent text-gray-500">Or continue with</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 w-full">
                <Button
                  type="button"
                  onClick={handleGoogleSignup}
                  className="bg-white/5 border border-white/10 hover:bg-white/10 text-white font-medium rounded-xl h-11"
                  disabled={isLoading}
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  </svg>
                  Google
                </Button>
                <Button
                  type="button"
                  onClick={handleGithubSignup}
                  className="bg-white/5 border border-white/10 hover:bg-white/10 text-white font-medium rounded-xl h-11"
                  disabled={isLoading}
                >
                  <svg className="w-5 h-5 mr-2 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                  GitHub
                </Button>
              </div>

              <div className="text-center text-sm text-gray-400 mt-4">
                Already have an account?{' '}
                <Link to="/login" className="text-purple-400 hover:text-white font-medium transition-colors">
                  Log in
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}