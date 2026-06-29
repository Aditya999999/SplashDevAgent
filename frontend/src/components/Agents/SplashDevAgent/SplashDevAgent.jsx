import React, { useState, useMemo } from 'react';
import { CommonAgent } from '../../CommonAgent/CommonAgent';
import { splashSendMessage, splashStartConversation } from './splashDevApiClient';

export const SplashDevAgent = ({ userId, workspace_id, agentId }) => {
    const [loopMode, setLoopMode] = useState('react'); // Default constraint: ReAct loop

    // Memoize the API configurations for CommonAgent decoupling patterns
    const apiConfig = useMemo(() => ({
        startConversation: splashStartConversation,
        sendMessage: async (payload) => {
            // Inject the selected loop mode parameters directly into outbound payload structure
            const enrichedPayload = {
                ...payload,
                loop_mode: loopMode
            };
            return await splashSendMessage(enrichedPayload);
        }
    }), [loopMode]);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Loop Mode Selector Header Panel */}
            <div style={{
                padding: '12px 20px',
                backgroundColor: '#181825',
                borderBottom: '1px solid #313244',
                display: 'flex',
                alignItems: 'center',
                gap: '15px'
            }}>
                <strong style={{ color: '#cdd6f4', fontSize: '14px' }}>Loop Execution Paradigm:</strong>
                <div style={{ display: 'flex', gap: '8px' }}>
                    {['react', 'ralph', 'deep'].map(mode => (
                        <button
                            key={mode}
                            onClick={() => setLoopMode(mode)}
                            style={{
                                padding: '6px 14px',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '13px',
                                fontWeight: 'bold',
                                textTransform: 'uppercase',
                                backgroundColor: loopMode === mode ? '#89b4fa' : '#313244',
                                color: loopMode === mode ? '#11111b' : '#cdd6f4',
                                border: 'none',
                                transition: 'all 0.2s ease'
                            }}
                        >
                            {mode} mode
                        </button>
                    ))}
                </div>
            </div>
            
            <div style={{ flex: 1 }}>
                <CommonAgent
                    agentId={agentId || 'developer'}
                    userId={userId || 'user_dev'}
                    workspace_id={workspace_id || 'workspace_dev'}
                    apiConfig={apiConfig}
                    showFileUpload={true}
                    isLLMRouterEnabled={true}
                />
            </div>
        </div>
    );
};

export default SplashDevAgent;
