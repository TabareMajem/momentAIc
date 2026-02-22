import React, { useState, useEffect } from 'react';

interface Character {
    id: string;
    name: string;
    handle: string | null;
    tagline: string | null;
    status: string;
    persona: Record<string, any>;
    visual_identity: Record<string, any>;
    platforms: Record<string, any>;
    performance_metrics: Record<string, any> | null;
    autonomy_level: string;
    daily_budget_usd: number | null;
    total_spent_usd: number;
    created_at: string;
    character_dna?: string | null;
}

interface ContentPiece {
    id: string;
    platform: string;
    content_type: string;
    content_data: Record<string, any>;
    status: string;
    virality_score: number | null;
    cost_usd: number;
    created_at: string;
}

const API_BASE = '/api/v1/characters';

const STATUS_COLORS: Record<string, { bg: string; text: string; dot: string }> = {
    active: { bg: 'rgba(52, 211, 153, 0.15)', text: '#34d399', dot: '#34d399' },
    draft: { bg: 'rgba(251, 191, 36, 0.15)', text: '#fbbf24', dot: '#fbbf24' },
    paused: { bg: 'rgba(156, 163, 175, 0.15)', text: '#9ca3af', dot: '#9ca3af' },
    retired: { bg: 'rgba(239, 68, 68, 0.15)', text: '#ef4444', dot: '#ef4444' },
};

const PLATFORM_ICONS: Record<string, string> = {
    tiktok: '🎵',
    instagram: '📸',
    twitter: '𝕏',
    linkedin: '💼',
    youtube_shorts: '▶️',
};

const AUTONOMY_LABELS: Record<string, string> = {
    L1: 'Manual',
    L2: 'Semi-Auto',
    L3: 'Auto',
    L4: 'Full Auto',
};

export default function CharacterFactory() {
    const [characters, setCharacters] = useState<Character[]>([]);
    const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
    const [content, setContent] = useState<ContentPiece[]>([]);
    const [showCreateWizard, setShowCreateWizard] = useState(false);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [activeTab, setActiveTab] = useState<'overview' | 'content' | 'analytics' | 'dna'>('overview');

    // Create wizard state
    const [wizardStep, setWizardStep] = useState(0);
    const [wizardData, setWizardData] = useState({
        name: '',
        target_audience: '',
        brand_personality: '',
        visual_direction: '',
        voice_direction: '',
        platform_focus: 'tiktok,instagram',
        product_to_promote: '',
    });

    // Using hardcoded startup ID for now — in production this comes from auth context
    const startupId = localStorage.getItem('selected_startup_id') || '';

    useEffect(() => {
        if (startupId) fetchCharacters();
    }, [startupId]);

    const fetchCharacters = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('access_token');
            const res = await fetch(`${API_BASE}/${startupId}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (res.ok) {
                const data = await res.json();
                setCharacters(data);
            }
        } catch (e) {
            console.error('Failed to fetch characters', e);
        } finally {
            setLoading(false);
        }
    };

    const fetchContent = async (charId: string) => {
        try {
            const token = localStorage.getItem('access_token');
            const res = await fetch(`${API_BASE}/${startupId}/${charId}/content`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (res.ok) setContent(await res.json());
        } catch (e) {
            console.error('Failed to fetch content', e);
        }
    };

    const createCharacter = async () => {
        try {
            setGenerating(true);
            const token = localStorage.getItem('access_token');
            const res = await fetch(`${API_BASE}/${startupId}`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify(wizardData),
            });
            if (res.ok) {
                const newChar = await res.json();
                setCharacters((prev) => [newChar, ...prev]);
                setShowCreateWizard(false);
                setWizardStep(0);
                setSelectedCharacter(newChar);
            }
        } catch (e) {
            console.error('Failed to create character', e);
        } finally {
            setGenerating(false);
        }
    };

    const toggleCharacterStatus = async (char: Character) => {
        const action = char.status === 'active' ? 'pause' : 'activate';
        try {
            const token = localStorage.getItem('access_token');
            const res = await fetch(`${API_BASE}/${startupId}/${char.id}/${action}`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
            });
            if (res.ok) {
                const updated = await res.json();
                setCharacters((prev) => prev.map((c) => (c.id === char.id ? updated : c)));
                if (selectedCharacter?.id === char.id) setSelectedCharacter(updated);
            }
        } catch (e) {
            console.error('Failed to toggle status', e);
        }
    };

    const generateContent = async (charId: string, platform = 'tiktok') => {
        try {
            setGenerating(true);
            const token = localStorage.getItem('access_token');
            const res = await fetch(`${API_BASE}/${startupId}/${charId}/generate-content`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ platform, funnel_stage: 'awareness' }),
            });
            if (res.ok) {
                await fetchContent(charId);
            }
        } catch (e) {
            console.error('Failed to generate content', e);
        } finally {
            setGenerating(false);
        }
    };

    // ─── Create Wizard ──────────────────────────────────────────────────────

    const wizardSteps = [
        {
            title: 'Identity Protocol',
            subtitle: 'Initiate core parameters',
            fields: [
                { key: 'name', label: 'Unit Designation (Name)', placeholder: 'e.g., Mika Wellness', type: 'text' },
                { key: 'target_audience', label: 'Infiltration Target', placeholder: 'e.g., Gen Z women dealing with anxiety, 18-28', type: 'textarea' },
            ],
        },
        {
            title: 'Psychology Matrix',
            subtitle: 'Inject personality algorithms',
            fields: [
                { key: 'brand_personality', label: 'Behavioral Traits', placeholder: 'e.g., Warm, vulnerable, subtly funny', type: 'textarea' },
                { key: 'product_to_promote', label: 'Payload (Product)', placeholder: 'e.g., MomentAIc wellness app', type: 'text' },
            ],
        },
        {
            title: 'Synthetic Generation',
            subtitle: 'Powered by Nano Banana Pro & ElevenLabs',
            fields: [
                { key: 'visual_direction', label: 'Visual Genome (Nano Banana)', placeholder: 'e.g., Cozy minimalist, earth tones', type: 'text' },
                { key: 'voice_direction', label: 'Vocal Signature (ElevenLabs)', placeholder: 'e.g., Calm, warm, slightly breathy', type: 'text' },
            ],
        },
        {
            title: 'Deployment Vectors',
            subtitle: 'Select network infiltration points',
            fields: [
                { key: 'platform_focus', label: 'Target Platforms', placeholder: 'tiktok,instagram,twitter', type: 'text' },
            ],
        },
    ];

    const renderCreateWizard = () => (
        <div style={styles.wizardOverlay}>
            <div style={{ ...styles.wizardCard, background: '#0a0a0a', border: '1px solid rgba(0,240,255,0.3)', boxShadow: '0 0 30px rgba(0,240,255,0.1)' }}>
                <div style={styles.wizardHeader}>
                    <h2 style={{ ...styles.wizardTitle, color: '#00f0ff', textTransform: 'uppercase', letterSpacing: '2px' }}>
                        <span style={{ marginRight: 8 }}>⚡</span> Synthesize Employee
                    </h2>
                    <button onClick={() => setShowCreateWizard(false)} style={styles.closeBtn}>✕</button>
                </div>

                {/* Progress bar */}
                <div style={styles.progressBar}>
                    {wizardSteps.map((step, i) => (
                        <div
                            key={i}
                            style={{
                                ...styles.progressDot,
                                backgroundColor: i <= wizardStep ? '#00f0ff' : '#1f2937',
                                boxShadow: i <= wizardStep ? '0 0 10px #00f0ff' : 'none',
                                flex: i < wizardSteps.length - 1 ? 1 : 0,
                            }}
                        />
                    ))}
                </div>
                <div style={{ ...styles.stepLabel, color: '#e5e7eb' }}>
                    Phase {wizardStep + 1}: <span style={{ color: '#00f0ff' }}>{wizardSteps[wizardStep].title}</span>
                </div>
                <p style={{ ...styles.stepSubtitle, color: '#9ca3af' }}>{wizardSteps[wizardStep].subtitle}</p>

                {/* Fields */}
                <div style={styles.fieldsGrid}>
                    {wizardSteps[wizardStep].fields.map((field) => (
                        <div key={field.key} style={styles.fieldGroup}>
                            <label style={{ ...styles.fieldLabel, color: '#9ca3af', textTransform: 'uppercase', fontSize: '10px' }}>{field.label}</label>
                            {field.type === 'textarea' ? (
                                <textarea
                                    style={{ ...styles.textarea, background: '#111', border: '1px solid #333', color: '#fff' }}
                                    placeholder={field.placeholder}
                                    value={(wizardData as any)[field.key]}
                                    onChange={(e) => setWizardData({ ...wizardData, [field.key]: e.target.value })}
                                    rows={3}
                                />
                            ) : (
                                <input
                                    style={{ ...styles.input, background: '#111', border: '1px solid #333', color: '#fff' }}
                                    type="text"
                                    placeholder={field.placeholder}
                                    value={(wizardData as any)[field.key]}
                                    onChange={(e) => setWizardData({ ...wizardData, [field.key]: e.target.value })}
                                />
                            )}
                        </div>
                    ))}
                    {wizardStep === 2 && (
                        <div style={{ marginTop: 16, padding: 12, background: 'rgba(52,211,153,0.1)', border: '1px solid rgba(52,211,153,0.3)', borderRadius: 8 }}>
                            <p style={{ fontSize: 12, color: '#34d399', margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
                                <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', background: '#34d399', animation: 'pulse 2s infinite' }} />
                                Live API Connections: Nano Banana Pro & ElevenLabs active.
                            </p>
                        </div>
                    )}
                </div>

                {/* Navigation */}
                <div style={styles.wizardNav}>
                    {wizardStep > 0 && (
                        <button onClick={() => setWizardStep(wizardStep - 1)} style={{ ...styles.secondaryBtn, color: '#9ca3af', border: '1px solid #333' }}>
                            ← Revert
                        </button>
                    )}
                    <div style={{ flex: 1 }} />
                    {wizardStep < wizardSteps.length - 1 ? (
                        <button onClick={() => setWizardStep(wizardStep + 1)} style={{ ...styles.primaryBtn, background: 'rgba(0,240,255,0.1)', color: '#00f0ff', border: '1px solid #00f0ff' }}>
                            Compile Phase →
                        </button>
                    ) : (
                        <button onClick={createCharacter} disabled={generating} style={{ ...styles.createBtn, background: '#00f0ff', color: '#000', fontWeight: 'bold' }}>
                            {generating ? '🧬 Synthesizing DNA...' : '⚡ INITIALIZE UNIT'}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );

    // ─── Character Card ─────────────────────────────────────────────────────

    const renderCharacterCard = (char: Character) => {
        const statusStyle = STATUS_COLORS[char.status] || STATUS_COLORS.draft;
        const enabledPlatforms = Object.entries(char.platforms || {})
            .filter(([_, config]) => config?.enabled)
            .map(([name]) => name);

        return (
            <div
                key={char.id}
                style={{
                    ...styles.characterCard,
                    borderColor: selectedCharacter?.id === char.id ? '#8b5cf6' : '#1f2937',
                }}
                onClick={() => {
                    setSelectedCharacter(char);
                    fetchContent(char.id);
                }}
            >
                {/* Avatar placeholder */}
                <div style={styles.avatarSection}>
                    <div style={styles.avatar}>
                        {char.visual_identity?.identity_anchor_url ? (
                            <img
                                src={char.visual_identity.identity_anchor_url}
                                alt={char.name}
                                style={styles.avatarImg}
                            />
                        ) : (
                            <span style={styles.avatarEmoji}>
                                {char.name.charAt(0).toUpperCase()}
                            </span>
                        )}
                    </div>
                    <div style={{ ...styles.statusBadge, ...statusStyle }}>
                        <span style={{ ...styles.statusDot, backgroundColor: statusStyle.dot }} />
                        {char.status}
                    </div>
                </div>

                {/* Info */}
                <h3 style={styles.charName}>{char.name}</h3>
                <p style={styles.charHandle}>{char.handle}</p>
                {char.tagline && <p style={styles.charTagline}>{char.tagline}</p>}

                {/* Platforms */}
                <div style={styles.platformsRow}>
                    {enabledPlatforms.map((p) => (
                        <span key={p} style={styles.platformChip} title={p}>
                            {PLATFORM_ICONS[p] || '🌐'} {p}
                        </span>
                    ))}
                </div>

                {/* Stats */}
                <div style={styles.statsRow}>
                    <div style={styles.stat}>
                        <span style={styles.statValue}>${char.total_spent_usd.toFixed(2)}</span>
                        <span style={styles.statLabel}>Spent</span>
                    </div>
                    <div style={styles.stat}>
                        <span style={styles.statValue}>{AUTONOMY_LABELS[char.autonomy_level] || char.autonomy_level}</span>
                        <span style={styles.statLabel}>Mode</span>
                    </div>
                </div>

                {/* Actions */}
                <div style={styles.cardActions}>
                    <button
                        onClick={(e) => { e.stopPropagation(); toggleCharacterStatus(char); }}
                        style={{
                            ...styles.actionBtn,
                            backgroundColor: char.status === 'active' ? 'rgba(239,68,68,0.2)' : 'rgba(52,211,153,0.2)',
                            color: char.status === 'active' ? '#ef4444' : '#34d399',
                        }}
                    >
                        {char.status === 'active' ? '⏸ TERMINATE' : '▶ ACTIVATE'}
                    </button>
                    <button
                        onClick={(e) => { e.stopPropagation(); generateContent(char.id); }}
                        disabled={generating}
                        style={{ ...styles.actionBtn, backgroundColor: 'rgba(0,240,255,0.1)', color: '#00f0ff', border: '1px solid #00f0ff' }}
                    >
                        {generating ? '⏳' : '⚡'} DEPLOY SWARM
                    </button>
                </div>
            </div>
        );
    };

    // ─── Detail Panel ───────────────────────────────────────────────────────

    const renderDetailPanel = () => {
        if (!selectedCharacter) return (
            <div style={styles.emptyDetail}>
                <span style={{ fontSize: 48, marginBottom: 16 }}>🎭</span>
                <h3 style={{ color: '#9ca3af', margin: 0 }}>Select a character</h3>
                <p style={{ color: '#6b7280', fontSize: 14 }}>Click on a character card to view details</p>
            </div>
        );

        const char = selectedCharacter;
        const persona = char.persona || {};

        return (
            <div style={styles.detailPanel}>
                {/* Detail Header */}
                <div style={styles.detailHeader}>
                    <div style={styles.detailAvatar}>
                        {char.visual_identity?.identity_anchor_url ? (
                            <img src={char.visual_identity.identity_anchor_url} alt={char.name} style={styles.avatarImg} />
                        ) : (
                            <span style={{ ...styles.avatarEmoji, fontSize: 32 }}>{char.name.charAt(0)}</span>
                        )}
                    </div>
                    <div>
                        <h2 style={styles.detailName}>{char.name}</h2>
                        <p style={styles.detailHandle}>{char.handle}</p>
                    </div>
                </div>

                {/* Tabs */}
                <div style={styles.tabs}>
                    {(['overview', 'content', 'analytics', 'dna'] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            style={{
                                ...styles.tab,
                                borderBottomColor: activeTab === tab ? '#00f0ff' : 'transparent',
                                color: activeTab === tab ? '#00f0ff' : '#9ca3af',
                                textTransform: 'uppercase',
                                letterSpacing: '1px',
                                fontSize: '12px',
                                fontWeight: activeTab === tab ? 'bold' : 'normal'
                            }}
                        >
                            {tab === 'overview' && '📊 '}
                            {tab === 'content' && '📝 '}
                            {tab === 'analytics' && '📈 '}
                            {tab === 'dna' && '🧬 '}
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <div style={styles.tabContent}>
                    {activeTab === 'overview' && (
                        <>
                            {/* Persona */}
                            <div style={styles.section}>
                                <h4 style={styles.sectionTitle}>Persona</h4>
                                <div style={styles.metaGrid}>
                                    <div style={styles.metaItem}>
                                        <span style={styles.metaLabel}>Age</span>
                                        <span style={styles.metaValue}>{persona.age || 'N/A'}</span>
                                    </div>
                                    <div style={styles.metaItem}>
                                        <span style={styles.metaLabel}>Location</span>
                                        <span style={styles.metaValue}>{persona.location || 'N/A'}</span>
                                    </div>
                                    <div style={styles.metaItem}>
                                        <span style={styles.metaLabel}>Occupation</span>
                                        <span style={styles.metaValue}>{persona.occupation || 'N/A'}</span>
                                    </div>
                                    <div style={styles.metaItem}>
                                        <span style={styles.metaLabel}>Humor</span>
                                        <span style={styles.metaValue}>{persona.humor_style || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Personality Traits */}
                            {persona.personality_traits && (
                                <div style={styles.section}>
                                    <h4 style={styles.sectionTitle}>Personality Traits</h4>
                                    <div style={styles.chipContainer}>
                                        {(persona.personality_traits || []).map((trait: string, i: number) => (
                                            <span key={i} style={styles.traitChip}>{trait}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Voice Examples */}
                            {persona.voice_examples?.length > 0 && (
                                <div style={styles.section}>
                                    <h4 style={styles.sectionTitle}>Voice Examples</h4>
                                    {persona.voice_examples.slice(0, 3).map((example: string, i: number) => (
                                        <div key={i} style={styles.voiceExample}>
                                            "{example}"
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Budget */}
                            <div style={styles.section}>
                                <h4 style={styles.sectionTitle}>Budget & Autonomy</h4>
                                <div style={styles.metaGrid}>
                                    <div style={styles.metaItem}>
                                        <span style={styles.metaLabel}>Daily Budget</span>
                                        <span style={styles.metaValue}>${char.daily_budget_usd?.toFixed(2) || '∞'}</span>
                                    </div>
                                    <div style={styles.metaItem}>
                                        <span style={styles.metaLabel}>Total Spent</span>
                                        <span style={styles.metaValue}>${char.total_spent_usd.toFixed(2)}</span>
                                    </div>
                                    <div style={styles.metaItem}>
                                        <span style={styles.metaLabel}>Autonomy</span>
                                        <span style={styles.metaValue}>{AUTONOMY_LABELS[char.autonomy_level]}</span>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}

                    {activeTab === 'content' && (
                        <div>
                            <div style={styles.contentActions}>
                                <button
                                    onClick={() => generateContent(char.id, 'tiktok')}
                                    disabled={generating}
                                    style={{ ...styles.generateBtn, background: 'rgba(0,240,255,0.1)', color: '#00f0ff', border: '1px solid #00f0ff', boxShadow: '0 0 10px rgba(0,240,255,0.2)' }}
                                >
                                    {generating ? '⏳ DEPLOYING SWARM...' : '⚡ INITIATE CONTENT SWARM'}
                                </button>
                            </div>
                            {content.length === 0 ? (
                                <div style={styles.emptyContent}>
                                    <span style={{ fontSize: 36 }}>📝</span>
                                    <p style={{ color: '#6b7280' }}>No content yet. Click generate to create your first post!</p>
                                </div>
                            ) : (
                                content.map((piece) => (
                                    <div key={piece.id} style={styles.contentCard}>
                                        <div style={styles.contentHeader}>
                                            <span style={styles.platformChip}>
                                                {PLATFORM_ICONS[piece.platform]} {piece.platform}
                                            </span>
                                            <span style={{
                                                ...styles.contentStatus,
                                                color: piece.status === 'published' ? '#34d399' : '#fbbf24',
                                            }}>
                                                {piece.status}
                                            </span>
                                            {piece.virality_score != null && (
                                                <span style={{
                                                    ...styles.viralityScore,
                                                    color: piece.virality_score >= 70 ? '#ef4444' : piece.virality_score >= 50 ? '#fbbf24' : '#9ca3af',
                                                }}>
                                                    🔥 {piece.virality_score}
                                                </span>
                                            )}
                                        </div>
                                        <p style={styles.contentScript}>
                                            {piece.content_data?.script?.substring(0, 200) || piece.content_data?.caption || 'No script'}
                                            {(piece.content_data?.script?.length || 0) > 200 && '...'}
                                        </p>
                                        <div style={styles.contentMeta}>
                                            <span>${piece.cost_usd.toFixed(3)}</span>
                                            <span>{new Date(piece.created_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    {activeTab === 'analytics' && (
                        <div style={styles.emptyContent}>
                            <span style={{ fontSize: 36 }}>📈</span>
                            <p style={{ color: '#6b7280' }}>
                                Analytics will populate once content is published and engagement data flows in.
                            </p>
                            {char.performance_metrics && (
                                <pre style={styles.jsonBlock}>
                                    {JSON.stringify(char.performance_metrics, null, 2)}
                                </pre>
                            )}
                        </div>
                    )}

                    {activeTab === 'dna' && (
                        <div style={styles.dnaSection}>
                            {char.character_dna ? (
                                <pre style={styles.dnaContent}>{char.character_dna}</pre>
                            ) : (
                                <p style={{ color: '#6b7280' }}>DNA document will be generated when the character is created.</p>
                            )}
                        </div>
                    )}
                </div>
            </div>
        );
    };

    // ─── Main Render ────────────────────────────────────────────────────────

    if (!startupId) {
        return (
            <div style={styles.container}>
                <div style={styles.emptyDetail}>
                    <span style={{ fontSize: 48 }}>⚡</span>
                    <h2 style={{ color: '#00f0ff', textTransform: 'uppercase', letterSpacing: '2px' }}>Synthetic Employee Factory</h2>
                    <p style={{ color: '#9ca3af' }}>SYSTEM OFFLINE: Initialized Empire Required.</p>
                </div>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            {/* Header */}
            <div style={styles.header}>
                <div>
                    <h1 style={{ ...styles.title, color: '#00f0ff', textTransform: 'uppercase', letterSpacing: '2px' }}>
                        <span style={styles.titleIcon}>⚡</span> Synthetic Employee Factory
                    </h1>
                    <p style={styles.subtitle}>
                        Design, deploy, and monitor fully autonomous digital workers for your empire.
                    </p>
                </div>
                <button onClick={() => setShowCreateWizard(true)} style={{ ...styles.createCharBtn, background: 'rgba(0,240,255,0.1)', color: '#00f0ff', border: '1px solid #00f0ff', boxShadow: '0 0 15px rgba(0,240,255,0.2)' }}>
                    + SYNTHESIZE NEW UNIT
                </button>
            </div>

            {/* Content */}
            <div style={styles.mainGrid}>
                {/* Character List */}
                <div style={styles.characterList}>
                    {loading ? (
                        <div style={styles.loadingState}>
                            <div style={styles.spinner} />
                            <p style={{ color: '#9ca3af' }}>Loading characters...</p>
                        </div>
                    ) : characters.length === 0 ? (
                        <div style={styles.emptyCharacters}>
                            <span style={{ fontSize: 48 }}>🎭</span>
                            <h3 style={{ color: '#e5e7eb', margin: '16px 0 8px' }}>No characters yet</h3>
                            <p style={{ color: '#6b7280', fontSize: 14, marginBottom: 16 }}>
                                Create your first AI influencer to start generating viral content
                            </p>
                            <button onClick={() => setShowCreateWizard(true)} style={styles.createCharBtn}>
                                ✨ Create First Character
                            </button>
                        </div>
                    ) : (
                        characters.map(renderCharacterCard)
                    )}
                </div>

                {/* Detail Panel */}
                <div style={styles.detailArea}>
                    {renderDetailPanel()}
                </div>
            </div>

            {/* Create Wizard Modal */}
            {showCreateWizard && renderCreateWizard()}
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// STYLES
// ═══════════════════════════════════════════════════════════════════════════════

const styles: Record<string, React.CSSProperties> = {
    container: {
        padding: '24px 32px',
        minHeight: '100vh',
        backgroundColor: '#0f1117',
        color: '#e5e7eb',
        fontFamily: "'Inter', -apple-system, sans-serif",
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 32,
    },
    title: {
        fontSize: 28,
        fontWeight: 700,
        margin: 0,
        background: 'linear-gradient(135deg, #a78bfa, #ec4899)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
    },
    titleIcon: {
        WebkitTextFillColor: 'initial',
    },
    subtitle: {
        color: '#6b7280',
        margin: '4px 0 0',
        fontSize: 14,
    },
    createCharBtn: {
        background: 'linear-gradient(135deg, #8b5cf6, #ec4899)',
        color: 'white',
        border: 'none',
        borderRadius: 12,
        padding: '12px 24px',
        fontSize: 15,
        fontWeight: 600,
        cursor: 'pointer',
        transition: 'transform 0.15s, opacity 0.15s',
    },
    mainGrid: {
        display: 'grid',
        gridTemplateColumns: '380px 1fr',
        gap: 24,
        alignItems: 'start',
    },
    characterList: {
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
    },
    characterCard: {
        background: '#1a1d27',
        borderRadius: 16,
        padding: 20,
        border: '1px solid #1f2937',
        cursor: 'pointer',
        transition: 'border-color 0.2s, transform 0.15s',
    },
    avatarSection: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 12,
    },
    avatar: {
        width: 48,
        height: 48,
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #8b5cf6, #ec4899)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
    },
    avatarImg: {
        width: '100%',
        height: '100%',
        objectFit: 'cover' as const,
        borderRadius: '50%',
    },
    avatarEmoji: {
        fontSize: 24,
        color: 'white',
        fontWeight: 700,
    },
    statusBadge: {
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: '4px 10px',
        borderRadius: 20,
        fontSize: 12,
        fontWeight: 500,
        textTransform: 'capitalize' as const,
    },
    statusDot: {
        width: 6,
        height: 6,
        borderRadius: '50%',
        display: 'inline-block',
    },
    charName: {
        fontSize: 18,
        fontWeight: 600,
        margin: 0,
        color: '#e5e7eb',
    },
    charHandle: {
        color: '#6b7280',
        fontSize: 13,
        margin: '2px 0',
    },
    charTagline: {
        color: '#9ca3af',
        fontSize: 13,
        margin: '6px 0 12px',
        fontStyle: 'italic',
    },
    platformsRow: {
        display: 'flex',
        gap: 6,
        flexWrap: 'wrap' as const,
        marginBottom: 12,
    },
    platformChip: {
        background: '#111827',
        color: '#9ca3af',
        padding: '4px 8px',
        borderRadius: 6,
        fontSize: 11,
        fontWeight: 500,
    },
    statsRow: {
        display: 'flex',
        gap: 16,
        marginBottom: 12,
    },
    stat: {
        display: 'flex',
        flexDirection: 'column' as const,
    },
    statValue: {
        fontSize: 16,
        fontWeight: 600,
        color: '#a78bfa',
    },
    statLabel: {
        fontSize: 11,
        color: '#6b7280',
        textTransform: 'uppercase' as const,
        letterSpacing: 0.5,
    },
    cardActions: {
        display: 'flex',
        gap: 8,
    },
    actionBtn: {
        flex: 1,
        padding: '8px 12px',
        borderRadius: 8,
        border: 'none',
        fontSize: 13,
        fontWeight: 500,
        cursor: 'pointer',
        transition: 'opacity 0.15s',
    },
    detailArea: {
        minHeight: 600,
    },
    emptyDetail: {
        display: 'flex',
        flexDirection: 'column' as const,
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 400,
        background: '#1a1d27',
        borderRadius: 16,
        border: '1px solid #1f2937',
    },
    detailPanel: {
        background: '#1a1d27',
        borderRadius: 16,
        border: '1px solid #1f2937',
        overflow: 'hidden',
    },
    detailHeader: {
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        padding: '20px 24px',
        borderBottom: '1px solid #1f2937',
    },
    detailAvatar: {
        width: 56,
        height: 56,
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #8b5cf6, #ec4899)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
    },
    detailName: {
        margin: 0,
        fontSize: 22,
        fontWeight: 600,
    },
    detailHandle: {
        margin: 0,
        color: '#6b7280',
        fontSize: 14,
    },
    tabs: {
        display: 'flex',
        borderBottom: '1px solid #1f2937',
        padding: '0 24px',
    },
    tab: {
        background: 'none',
        border: 'none',
        borderBottom: '2px solid transparent',
        padding: '12px 16px',
        fontSize: 14,
        fontWeight: 500,
        cursor: 'pointer',
        transition: 'color 0.15s, border-color 0.15s',
    },
    tabContent: {
        padding: 24,
    },
    section: {
        marginBottom: 24,
    },
    sectionTitle: {
        fontSize: 13,
        fontWeight: 600,
        color: '#9ca3af',
        textTransform: 'uppercase' as const,
        letterSpacing: 1,
        marginBottom: 12,
    },
    metaGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
        gap: 12,
    },
    metaItem: {
        display: 'flex',
        flexDirection: 'column' as const,
        background: '#111827',
        padding: 12,
        borderRadius: 8,
    },
    metaLabel: {
        fontSize: 11,
        color: '#6b7280',
        textTransform: 'uppercase' as const,
        letterSpacing: 0.5,
    },
    metaValue: {
        fontSize: 15,
        fontWeight: 500,
        color: '#e5e7eb',
        marginTop: 4,
    },
    chipContainer: {
        display: 'flex',
        flexWrap: 'wrap' as const,
        gap: 6,
    },
    traitChip: {
        background: 'rgba(139, 92, 246, 0.15)',
        color: '#a78bfa',
        padding: '4px 10px',
        borderRadius: 20,
        fontSize: 12,
        fontWeight: 500,
    },
    voiceExample: {
        background: '#111827',
        padding: '10px 14px',
        borderRadius: 8,
        fontSize: 13,
        color: '#d1d5db',
        fontStyle: 'italic',
        marginBottom: 8,
        borderLeft: '3px solid #8b5cf6',
    },
    contentActions: {
        marginBottom: 16,
    },
    generateBtn: {
        background: 'linear-gradient(135deg, #8b5cf6, #ec4899)',
        color: 'white',
        border: 'none',
        borderRadius: 10,
        padding: '10px 20px',
        fontSize: 14,
        fontWeight: 600,
        cursor: 'pointer',
    },
    emptyContent: {
        display: 'flex',
        flexDirection: 'column' as const,
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 200,
        textAlign: 'center' as const,
    },
    contentCard: {
        background: '#111827',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        border: '1px solid #1f2937',
    },
    contentHeader: {
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        marginBottom: 8,
    },
    contentStatus: {
        fontSize: 12,
        fontWeight: 500,
        textTransform: 'capitalize' as const,
    },
    viralityScore: {
        marginLeft: 'auto',
        fontSize: 14,
        fontWeight: 600,
    },
    contentScript: {
        fontSize: 13,
        color: '#d1d5db',
        lineHeight: 1.5,
        margin: '8px 0',
    },
    contentMeta: {
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: 12,
        color: '#6b7280',
    },
    jsonBlock: {
        background: '#111827',
        padding: 16,
        borderRadius: 8,
        fontSize: 12,
        color: '#a78bfa',
        overflow: 'auto',
        maxHeight: 300,
        whiteSpace: 'pre-wrap' as const,
        textAlign: 'left' as const,
        width: '100%',
    },
    dnaSection: {
        padding: 0,
    },
    dnaContent: {
        background: '#111827',
        padding: 20,
        borderRadius: 12,
        fontSize: 13,
        color: '#d1d5db',
        lineHeight: 1.6,
        whiteSpace: 'pre-wrap' as const,
        overflow: 'auto',
        maxHeight: 600,
        fontFamily: "'JetBrains Mono', monospace",
    },

    // ─── Wizard Styles ───
    wizardOverlay: {
        position: 'fixed' as const,
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.7)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
    },
    wizardCard: {
        background: '#1a1d27',
        borderRadius: 20,
        padding: 32,
        width: '100%',
        maxWidth: 520,
        border: '1px solid #374151',
        boxShadow: '0 24px 64px rgba(0,0,0,0.5)',
    },
    wizardHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 24,
    },
    wizardTitle: {
        margin: 0,
        fontSize: 22,
        fontWeight: 700,
        background: 'linear-gradient(135deg, #a78bfa, #ec4899)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
    },
    closeBtn: {
        background: 'none',
        border: 'none',
        color: '#6b7280',
        fontSize: 20,
        cursor: 'pointer',
    },
    progressBar: {
        display: 'flex',
        gap: 4,
        marginBottom: 16,
    },
    progressDot: {
        height: 4,
        borderRadius: 2,
        minWidth: 12,
        transition: 'background-color 0.3s',
    },
    stepLabel: {
        fontSize: 14,
        fontWeight: 600,
        color: '#a78bfa',
        marginBottom: 4,
    },
    stepSubtitle: {
        color: '#6b7280',
        fontSize: 13,
        margin: '0 0 20px',
    },
    fieldsGrid: {
        display: 'flex',
        flexDirection: 'column' as const,
        gap: 16,
    },
    fieldGroup: {
        display: 'flex',
        flexDirection: 'column' as const,
        gap: 6,
    },
    fieldLabel: {
        fontSize: 13,
        fontWeight: 500,
        color: '#9ca3af',
    },
    input: {
        background: '#111827',
        border: '1px solid #374151',
        borderRadius: 10,
        padding: '10px 14px',
        fontSize: 14,
        color: '#e5e7eb',
        outline: 'none',
        transition: 'border-color 0.2s',
    },
    textarea: {
        background: '#111827',
        border: '1px solid #374151',
        borderRadius: 10,
        padding: '10px 14px',
        fontSize: 14,
        color: '#e5e7eb',
        outline: 'none',
        resize: 'vertical' as const,
        fontFamily: 'inherit',
    },
    wizardNav: {
        display: 'flex',
        gap: 12,
        marginTop: 24,
    },
    secondaryBtn: {
        background: '#1f2937',
        color: '#9ca3af',
        border: 'none',
        borderRadius: 10,
        padding: '10px 20px',
        fontSize: 14,
        fontWeight: 500,
        cursor: 'pointer',
    },
    primaryBtn: {
        background: '#8b5cf6',
        color: 'white',
        border: 'none',
        borderRadius: 10,
        padding: '10px 20px',
        fontSize: 14,
        fontWeight: 600,
        cursor: 'pointer',
    },
    createBtn: {
        background: 'linear-gradient(135deg, #8b5cf6, #ec4899)',
        color: 'white',
        border: 'none',
        borderRadius: 10,
        padding: '12px 24px',
        fontSize: 15,
        fontWeight: 600,
        cursor: 'pointer',
    },
    loadingState: {
        display: 'flex',
        flexDirection: 'column' as const,
        alignItems: 'center',
        padding: 48,
    },
    spinner: {
        width: 32,
        height: 32,
        border: '3px solid #1f2937',
        borderTopColor: '#8b5cf6',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
        marginBottom: 12,
    },
    emptyCharacters: {
        display: 'flex',
        flexDirection: 'column' as const,
        alignItems: 'center',
        padding: 48,
        background: '#1a1d27',
        borderRadius: 16,
        border: '1px dashed #374151',
        textAlign: 'center' as const,
    },
};
