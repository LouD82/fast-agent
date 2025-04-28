// Fast-Agent GUI JavaScript

// DOM Elements
const modelSelect = document.getElementById('model-select');
const showToolsCheckbox = document.getElementById('show-tools');
const showThinkingCheckbox = document.getElementById('show-thinking');
const clearBtn = document.getElementById('clear-btn');
const chatContainer = document.getElementById('chat-container');
const promptInput = document.getElementById('prompt-input');
const sendBtn = document.getElementById('send-btn');
const statusContainer = document.getElementById('status-container');

// WebSocket connection
let socket;
let isConnected = false;

// Initialize the application
function init() {
    // Load available models
    fetchModels();
    
    // Setup WebSocket connection
    connectWebSocket();
    
    // Setup event listeners
    setupEventListeners();
}

// Fetch available models from the API
async function fetchModels() {
    try {
        const response = await fetch('/models');
        const data = await response.json();
        
        // Populate model select dropdown
        data.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            modelSelect.appendChild(option);
        });
        
        // Select the first model by default
        if (data.models.length > 0) {
            modelSelect.value = data.models[0];
        }
    } catch (error) {
        console.error('Error fetching models:', error);
        updateStatus('Error loading models', 'error');
    }
}

// Connect to WebSocket server
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
        console.log('WebSocket connected');
        isConnected = true;
        updateStatus('Connected', 'success');
    };
    
    socket.onclose = () => {
        console.log('WebSocket disconnected');
        isConnected = false;
        updateStatus('Disconnected', 'error');
        
        // Try to reconnect after a delay
        setTimeout(connectWebSocket, 3000);
    };
    
    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus('Connection error', 'error');
    };
    
    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
    };
}

// Handle incoming WebSocket messages
function handleWebSocketMessage(message) {
    console.log('Received message:', message);
    
    switch (message.type) {
        case 'agent_response':
            addAssistantMessage(message.data.response);
            updateStatus('Ready', 'success');
            break;
            
        case 'error':
            addErrorMessage(message.data.message);
            updateStatus('Error', 'error');
            break;
            
        case 'tool_call':
            if (showToolsCheckbox.checked) {
                addToolCall(message.data);
            }
            break;
            
        case 'tool_result':
            if (showToolsCheckbox.checked) {
                addToolResult(message.data);
            }
            break;
            
        case 'thinking':
            if (showThinkingCheckbox.checked) {
                addThinking(message.data);
            }
            break;
            
        default:
            console.log('Unknown message type:', message.type);
    }
}

// Setup event listeners for UI elements
function setupEventListeners() {
    // Send button click
    sendBtn.addEventListener('click', sendPrompt);
    
    // Enter key in prompt input
    promptInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendPrompt();
        }
    });
    
    // Clear button click
    clearBtn.addEventListener('click', clearChat);
}

// Send prompt to the agent
function sendPrompt() {
    const prompt = promptInput.value.trim();
    const model = modelSelect.value;
    
    if (!prompt) {
        return;
    }
    
    if (!model) {
        updateStatus('Please select a model', 'error');
        return;
    }
    
    if (!isConnected) {
        updateStatus('Not connected to server', 'error');
        return;
    }
    
    // Add user message to chat
    addUserMessage(prompt);
    
    // Send message to server
    socket.send(JSON.stringify({
        type: 'run_agent',
        prompt: prompt,
        model: model
    }));
    
    // Clear input
    promptInput.value = '';
    
    // Update status
    updateStatus('Running...', 'running');
}

// Clear the chat
function clearChat() {
    chatContainer.innerHTML = `
        <div class="text-center text-gray-500 italic mt-32">
            Start a conversation with the agent
        </div>
    `;
    updateStatus('Ready', 'success');
}

// Add a user message to the chat
function addUserMessage(message) {
    // Remove placeholder if it exists
    if (chatContainer.querySelector('.text-center')) {
        chatContainer.innerHTML = '';
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = 'user-message';
    messageElement.textContent = message;
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add an assistant message to the chat
function addAssistantMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'assistant-message';
    messageElement.textContent = message;
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add a tool call to the chat
function addToolCall(data) {
    const messageElement = document.createElement('div');
    messageElement.className = 'tool-call';
    
    const toolName = document.createElement('div');
    toolName.className = 'font-bold';
    toolName.textContent = `Tool Call: ${data.tool_name}`;
    
    const toolArgs = document.createElement('pre');
    toolArgs.innerHTML = `<code>${JSON.stringify(data.tool_args, null, 2)}</code>`;
    
    messageElement.appendChild(toolName);
    messageElement.appendChild(toolArgs);
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add a tool result to the chat
function addToolResult(data) {
    const messageElement = document.createElement('div');
    messageElement.className = 'tool-result';
    
    const resultTitle = document.createElement('div');
    resultTitle.className = 'font-bold';
    resultTitle.textContent = 'Tool Result:';
    
    const resultContent = document.createElement('pre');
    resultContent.innerHTML = `<code>${JSON.stringify(data.content, null, 2)}</code>`;
    
    messageElement.appendChild(resultTitle);
    messageElement.appendChild(resultContent);
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add thinking/reasoning to the chat
function addThinking(data) {
    const messageElement = document.createElement('div');
    messageElement.className = 'thinking-message';
    messageElement.style.backgroundColor = '#f0f0f0';
    messageElement.style.borderLeft = '4px solid #d9d9d9';
    messageElement.style.padding = '10px';
    messageElement.style.marginBottom = '10px';
    messageElement.style.borderRadius = '4px';
    messageElement.style.fontStyle = 'italic';
    
    messageElement.textContent = data.thinking;
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add an error message to the chat
function addErrorMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'error-message';
    messageElement.textContent = `Error: ${message}`;
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Update the status display
function updateStatus(message, type = 'default') {
    statusContainer.textContent = message;
    
    // Remove existing status classes
    statusContainer.classList.remove('status-running', 'status-error', 'status-success');
    
    // Add appropriate class
    if (type === 'running') {
        statusContainer.classList.add('status-running', 'loading');
    } else if (type === 'error') {
        statusContainer.classList.add('status-error');
        statusContainer.classList.remove('loading');
    } else if (type === 'success') {
        statusContainer.classList.add('status-success');
        statusContainer.classList.remove('loading');
    } else {
        statusContainer.classList.remove('loading');
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init);
