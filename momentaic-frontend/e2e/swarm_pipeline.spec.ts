import { test, expect } from '@playwright/test';

test.describe('Zero-Cost End-to-End Pipeline Engine Tests', () => {
  let authToken: string;
  let testStartupId: string;
  const testEmail = `e2e_tester_${Date.now()}@momentaic.com`;

  test.beforeAll(async ({ request }) => {
    // 1. Create a fresh test user to secure a valid JWT token
    const signupRes = await request.post('/api/v1/auth/signup', {
      data: {
        email: testEmail,
        password: 'TestPassword123!',
        full_name: 'E2E Test User'
      }
    });
    
    // Depending on DB state, signup might fail if email exists, 
    // so we fallback to login if needed.
    if (signupRes.status() === 201) {
      const data = await signupRes.json();
      authToken = data.tokens.access_token;
      console.log('Signup success. Token attached.');
    } else {
      console.log('Signup skipped/failed (status:', signupRes.status(), '), falling back to login.');
      const loginRes = await request.post('/api/v1/auth/login', {
        data: {
          email: testEmail,
          password: 'TestPassword123!', full_name: 'E2E Tester'
        }
      });
      const data = await loginRes.json();
      console.log('Login status:', loginRes.status(), 'Data:', data);
      authToken = data.tokens.access_token;
    }
    
    expect(authToken).toBeDefined();
    
    // Create a mock startup for the test user to operate on
    const startupRes = await request.post('/api/v1/startups', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        name: 'E2E Mock Startup',
        description: 'Testing the agent swarms at zero cost.',
        industry: 'Software'
      }
    });
    
    expect(startupRes.status()).toBe(201);
    const startupData = await startupRes.json();
    testStartupId = startupData.id;
    console.log('Startup created with ID:', testStartupId);
  });

  test('Influencer Army Swarm Execution (Zero-Cost)', async ({ request }) => {
    // 1. Trigger the Swarm Pipeline Backend
    // Playwright config injects X-E2E-Test-Mode: true automatically into this request context.
    const swarmRes = await request.post('/api/v1/momentaic/campaigns/swarm/influencer-army', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        startup_id: testStartupId, // In a real suite, we'd capture the ID from the setup loop
        niche: 'B2B SaaS Founders in New York',
        region: 'US'
      }
    });
    
    // Expect the swarm orchestrator to accept the job
    expect(swarmRes.status()).toBe(200);
    const swarmStatus = await swarmRes.json();
    expect(swarmStatus.message).toContain('deployed');

    // 2. Wait for the Swarm to hit the zero-cost mocked LLMs and generate ActionItems
    // In production this takes ~60s, but with LLM stubs, it's <2s.
    // We poll the HitL queue.
    let pendingActions = [];
    for(let i=0; i<15; i++) {
        // We use a wildcard search or specific startup ID if we captured it
        // We'll just test the /actions global queue for the user to be safe if startup ID wasn't captured perfectly
        const queueRes = await request.get(`/api/v1/hitl/startups/${testStartupId}/actions?status_filter=pending`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        
        if (queueRes.status() === 200) {
            pendingActions = await queueRes.json();
            if (pendingActions.length > 0) break;
        }
        await new Promise(r => setTimeout(r, 2000));
    }

    // Agent pipeline should have generated at least 1 ActionItem for HitL
    expect(pendingActions.length).toBeGreaterThan(0);
    const testAction = pendingActions[0];
    
    // The zero-cost mock should have populated the deterministic content
    expect(testAction.payload.action_type).toBe('send_dm');

    // 3. Trigger Human-in-the-Loop Approval
    const approveRes = await request.post(`/api/v1/hitl/startups/${testStartupId}/actions/review`, {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        action_ids: [testAction.id],
        approve: true
      }
    });

    expect(approveRes.status()).toBe(200);
    const approveResult = await approveRes.json();
    
    // 4. Validate Zero-Cost Inteception worked successfully
    // The `_execute_approved_action` should have hit the AffiliateIntegration mock 
    // instead of Stripe Connect and returned a success confirmation dynamically.
    expect(approveResult.success).toBe(true);
  });
});
