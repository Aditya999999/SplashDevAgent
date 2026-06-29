import React, { useState, useEffect } from 'react';
import './CommonAgent.css';

export const CommonAgent = ({
    agentId,
    userId,
    workspace_id,
    apiConfig,
    showFileUpload = true,
    isLLMRouterEnabled = true,
    extraTopContent
}) => {
    const [sessions, setSessions] = useState([]);
    const [selectedSessionIdx, setSelectedSessionIdx] = useState(null);
    const [chatContent, setChatContent] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);

    // Initial mock session
    useEffect(() => {
        setSessions([
            { id: 'session_1', title: 'Refactor Auth Microservice' },
            { id: 'session_2', title: 'Setup Unit Testing Suite' }
        ]);
        setSelectedSessionIdx('session_1');
    }, []);

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;
        
        const userMsg = { role: 'user', content: inputValue };
        setChatContent(prev => [...prev, userMsg]);
        const currentInput = inputValue;
        setInputValue('');
        setLoading(true);

        try {
            // Invoke dynamic apiConfig sendMessage mapping
            const response = await apiConfig.sendMessage({
                user_id: userId || 'user_dev',
                user_message: currentInput,
                conversation_id: selectedSessionIdx || 'session_1',
                workspace_id: workspace_id || 'ws_dev',
            });

            if (response && response.content) {
                setChatContent(prev => [...prev, { role: 'assistant', content: response.content }]);
            } else {
                setChatContent(prev => [...prev, { role: 'assistant', content: 'Empty response returned from agent.' }]);
            }
        } catch (err) {
            setChatContent(prev => [...prev, { role: 'assistant', content: `Error: ${err.message || 'Failed to dispatch message.'}` }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="common-agent-root">
            <div className="sidebar-panel">
                <h3>Sessions History</h3>
                <div className="sessions-list">
                    {sessions.map(s => (
                        <div 
                            key={s.id} 
                            className={`session-item ${selectedSessionIdx === s.id ? 'active' : ''}`}
                            onClick={() => setSelectedSessionIdx(s.id)}
                        >
                            {s.title}
                        </div>
                    ))}
                </div>
            </div>
            <div className="main-chat-area">
                <div className="chat-header">
                    <h2>{agentId ? agentId.toUpperCase() : 'Splash Dev Agent'}</h2>
                </div>
                
                {extraTopContent && (
                    <div className="extra-content-mount">
                        {extraTopContent({ chatContent })}
                    </div>
                )}

                <div className="messages-grid">
                    {chatContent.length === 0 ? (
                        <div className="empty-state">
                            <p>Select loop configuration and type a message to start coding.</p>
                        </div>
                    ) : (
                        chatContent.map((msg, idx) => (
                            <div key={idx} className={`message-bubble ${msg.role}`}>
                                <strong>{msg.role === 'user' ? 'User' : 'Agent'}:</strong>
                                <pre className="message-content">{msg.content}</pre>
                            </div>
                        ))
                    )}
                    {loading && <div className="loader-anim">Agent is processing and executing loops...</div>}
                </div>

                <div className="chat-input-bar">
                    <input 
                        type="text" 
                        placeholder="Type standard developer instructions..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    />
                    <button onClick={handleSendMessage} disabled={loading}>Send</button>
                </div>
            </div>
        </div>
    );
};
