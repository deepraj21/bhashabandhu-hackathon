import React, { useState, useEffect } from 'react';
import axios from 'axios';

const keyValues = {
    "en": "English",
    "as": "Assamese",
    "bn": "Bengali",
    "brx": "Bodo",
    "doi": "Dogri",
    "gom": "Goan Konkani",
    "gu": "Gujarati",
    "hi": "Hindi",
    "kn": "Kannada",
    "ks": "Kashmiri",
    "mai": "Maithili",
    "ml": "Malayalam",
    "mni": "Manipuri",
    "mr": "Marathi",
    "ne": "Nepali",
    "or": "Oriya",
    "pa": "Punjabi",
    "sa": "Sanskrit",
    "sat": "Santali",
    "sd": "Sindhi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu"
};

const App = () => {
    const [chats, setChats] = useState([]);
    const [currentChat, setCurrentChat] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [targetLanguage, setTargetLanguage] = useState('hi');

    useEffect(() => {
        fetchChats();
    }, []);

    useEffect(() => {
        const fetchCurrentChat = async (chat_id) => {
            try {
                const response = await axios.get(`https://server-fast-api.onrender.com/get_chat_history/${chat_id}`);
                setCurrentChat(chat_id);
                setMessages(response.data.messages);
                localStorage.setItem('currentChat', chat_id);
            } catch (error) {
                console.error('Error fetching chat history:', error);
                localStorage.removeItem('currentChat');
                setCurrentChat(null);
                setMessages([]);
            }
        };

        const savedChatId = localStorage.getItem('currentChat');
        if (savedChatId) {
            fetchCurrentChat(savedChatId);
        }
    }, []);

    const fetchChats = async () => {
        try {
            const response = await axios.get('https://server-fast-api.onrender.com/get_chats/');
            setChats(response.data);
        } catch (error) {
            console.error('Error fetching chats:', error);
        }
    };

    const fetchChatHistory = async (chat_id) => {
        try {
            const response = await axios.get(`https://server-fast-api.onrender.com/get_chat_history/${chat_id}`);
            setCurrentChat(chat_id);
            setMessages(response.data.messages);
            localStorage.setItem('currentChat', chat_id); 
        } catch (error) {
            console.error('Error fetching chat history:', error);
        }
    };

    const startNewChat = async () => {
        try {
            const response = await axios.post('https://server-fast-api.onrender.com/new_chat/');
            fetchChats();
            fetchChatHistory(response.data.chat_id);
        } catch (error) {
            console.error('Error starting new chat:', error);
        }
    };

    const sendMessage = async () => {
        if (!newMessage.trim()) return;
        if (typeof currentChat !== 'string' || !currentChat.trim()) {
            console.error('Invalid chat_id:', currentChat);
            return;
        }
        try {
            const response = await axios.post('https://server-fast-api.onrender.com/send_message/', {
                chat_id: currentChat,
                user_message: newMessage
            });
            setMessages(response.data.messages);
            setNewMessage('');
        } catch (error) {
            console.error('Error sending message:', error);
            if (error.response) {
                console.error('Error details:', error.response.data);
            }
        }
    };

    const translateMessage = async (content) => {
        try {
            const response = await axios.post('https://server-fast-api.onrender.com/scaler/translate', {
                source_language: 'en',
                content: content,
                target_language: targetLanguage
            });
            return response.data.translated_content;
        } catch (error) {
            console.error('Error translating message:', error);
            return '';
        }
    };

    const handleTranslate = async (index) => {
        const message = messages[index];
        if (message.role === 'ai') {
            const translatedText = await translateMessage(message.content);
            const updatedMessages = [...messages];
            updatedMessages[index].translatedContent = translatedText;
            setMessages(updatedMessages);
        }
    };

    return (
        <div>
            <div>
                <h1>LawLingo Chat</h1>
                <button onClick={startNewChat}>New Chat</button>
                <div>
                    {Object.entries(chats).map(([chat_id, chat_title]) => (
                        <button key={chat_id} onClick={() => fetchChatHistory(chat_id)}>
                            {chat_title}
                        </button>
                    ))}
                </div>
                <div>
                    <h2>Messages</h2>
                    {messages.map((message, index) => (
                        <div key={index}>
                            <div>
                                <strong>{message.role}:</strong> {message.content}
                            </div>
                            {message.role === 'ai' && (
                                <div>
                                    <button onClick={() => handleTranslate(index)}>Translate</button>
                                    {message.translatedContent && (
                                        <div><strong>Translated:</strong> {message.translatedContent}</div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
                <div>
                    <h3>New Message</h3>
                    <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type your message..."
                        onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                    />
                    <button onClick={sendMessage}>Send</button>
                </div>
            </div>
            <div>
                <h3>Translate AI Response</h3>
                <label htmlFor="target-language">Target Language:</label>
                <select
                    id="target-language"
                    name="target-language"
                    value={targetLanguage}
                    onChange={(e) => setTargetLanguage(e.target.value)}
                >
                    {Object.entries(keyValues).map(([code, name]) => (
                        <option key={code} value={code}>{name}</option>
                    ))}
                </select>
            </div>
        </div>
    );
};

export default App;
