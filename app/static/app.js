// Tea Party Interactive Frontend
const API_URL = 'http://localhost:8000';
let ws = null;
let isRunning = false;
let currentTurn = 0;
let maxTurns = 20;
let characters = [];
let autoPlayInterval = null;

// Character emoji mapping
const characterEmojis = {
    'purple_person': '👤',
    'blue_hair': '💙',
    'blonde_center': '✨',
    'gray_beard': '🧔',
    'phone_person': '📱'
};

// Initialize app
async function init() {
    await loadCharacters();
    renderCharacters();
    setupEventListeners();
    connectWebSocket();
}

// Load characters from API
async function loadCharacters() {
    try {
        const response = await fetch(`${API_URL}/api/characters`);
        const data = await response.json();
        characters = data.characters;
    } catch (error) {
        console.error('Failed to load characters:', error);
        showStatus('Error loading characters', 'error');
    }
}

// Render character cards with dials
function renderCharacters() {
    const container = document.getElementById('characters-list');
    container.innerHTML = '';

    characters.forEach(char => {
        const card = document.createElement('div');
        card.className = 'character-card';
        card.id = `char-${char.character_id}`;

        const emoji = characterEmojis[char.character_id] || '👤';

        card.innerHTML = `
            <div class="character-header">
                <div class="character-avatar">${emoji}</div>
                <div class="character-info">
                    <h3>${char.character_name}</h3>
                    <p>${char.character_id.replace('_', ' ')}</p>
                </div>
            </div>

            ${Object.keys(char.dial_values).map(dimension => `
                <div class="dial">
                    <div class="dial-label">
                        <span>${formatDimensionName(dimension)}</span>
                        <span class="dial-value" id="${char.character_id}-${dimension}-value">
                            ${Math.round(char.dial_values[dimension] * 100)}%
                        </span>
                    </div>
                    <input 
                        type="range" 
                        class="slider" 
                        min="0" 
                        max="100" 
                        value="${char.dial_values[dimension] * 100}"
                        data-character="${char.character_id}"
                        data-dimension="${dimension}"
                    >
                </div>
            `).join('')}
        `;

        container.appendChild(card);
    });

    // Add slider event listeners
    document.querySelectorAll('.slider').forEach(slider => {
        slider.addEventListener('input', handleDialChange);
    });
}

// Handle dial changes
async function handleDialChange(event) {
    const characterId = event.target.dataset.character;
    const dimension = event.target.dataset.dimension;
    const value = parseInt(event.target.value) / 100;

    // Update display
    document.getElementById(`${characterId}-${dimension}-value`).textContent = 
        `${Math.round(value * 100)}%`;

    // Highlight active character
    document.querySelectorAll('.character-card').forEach(card => {
        card.classList.remove('active');
    });
    document.getElementById(`char-${characterId}`).classList.add('active');

    // Send to API
    try {
        const response = await fetch(`${API_URL}/api/dial`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                character_id: characterId,
                dimension: dimension,
                value: value
            })
        });

        if (response.ok) {
            showStatus(`Updated ${formatDimensionName(dimension)} for ${getCharacterName(characterId)}`, 'success');
        }
    } catch (error) {
        console.error('Failed to update dial:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('start-btn').addEventListener('click', startConversation);
    document.getElementById('stop-btn').addEventListener('click', stopConversation);
    document.getElementById('clear-btn').addEventListener('click', clearConversation);
    document.getElementById('test-all-btn').addEventListener('click', testAllModels);
}

// Start auto-play conversation
async function startConversation() {
    if (isRunning) return;

    isRunning = true;
    currentTurn = 0;
    document.getElementById('start-btn').style.display = 'none';
    document.getElementById('stop-btn').style.display = 'inline-block';

    const topic = document.getElementById('topic-input').value || 'tea and pastries';
    showStatus(`Starting conversation about: ${topic}`, 'info');

    // Set topic
    try {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                action: 'set_topic',
                topic: topic
            }));
        }
    } catch (error) {
        console.error('Failed to set topic:', error);
    }

    // Start auto-play loop
    runAutoPlay();
}

// Stop conversation
function stopConversation() {
    isRunning = false;
    if (autoPlayInterval) {
        clearTimeout(autoPlayInterval);
        autoPlayInterval = null;
    }
    document.getElementById('start-btn').style.display = 'inline-block';
    document.getElementById('stop-btn').style.display = 'none';
    showStatus('Conversation paused', 'info');
}

// Auto-play loop - generates turns automatically
async function runAutoPlay() {
    if (!isRunning || currentTurn >= maxTurns) {
        stopConversation();
        showStatus('Conversation complete!', 'success');
        return;
    }

    // Pick next character (rotate through all 5)
    const characterIndex = currentTurn % characters.length;
    const character = characters[characterIndex];

    // Get selected model and video setting
    const model = document.getElementById('model-select').value;
    const generateVideo = document.getElementById('video-toggle').checked;

    // Highlight speaking character
    document.querySelectorAll('.character-card').forEach(card => {
        card.classList.remove('active');
    });
    document.getElementById(`char-${character.character_id}`).classList.add('active');

    const statusMsg = generateVideo 
        ? `${character.character_name} is speaking (${model}) + generating video...`
        : `${character.character_name} is speaking (${model})...`;
    showStatus(statusMsg, 'speaking');

    // Generate response
    try {
        const response = await fetch(`${API_URL}/api/conversation/turn`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                character_id: character.character_id,
                context: null,
                generate_video: generateVideo,
                model: model
            })
        });

        if (response.ok) {
            const data = await response.json();
            addMessage(data.turn);
            currentTurn++;
            updateTurnCount();

            // Continue after a delay
            autoPlayInterval = setTimeout(runAutoPlay, 2000); // 2 second delay between turns
        } else {
            throw new Error('Failed to generate response');
        }
    } catch (error) {
        console.error('Error generating turn:', error);
        showStatus('Error generating response', 'error');
        stopConversation();
    }
}

// Add message to conversation feed
function addMessage(turn) {
    const feed = document.getElementById('conversation-feed');
    
    // Remove loading message if present
    if (feed.querySelector('.loading')) {
        feed.innerHTML = '';
    }

    const message = document.createElement('div');
    message.className = 'message';

    const emoji = characterEmojis[turn.character_id] || '👤';
    
    // Format dial values for display
    const dialInfo = Object.entries(turn.dial_values)
        .map(([key, val]) => `${formatDimensionName(key)}: ${Math.round(val * 100)}%`)
        .join(' | ');

    const modelName = turn.model || 'gpt-4';
    const modelClass = `model-${modelName}`;
    const modelLabel = {
        'gpt-4': '🤖 GPT-4',
        'claude': '🧠 Claude',
        'gemini': '✨ Gemini'
    }[modelName] || modelName;

    // Build video HTML if available
    let videoHtml = '';
    if (turn.video_url) {
        videoHtml = `
            <div class="message-video">
                <video controls>
                    <source src="${turn.video_url}" type="video/mp4">
                    Your browser doesn't support video playback.
                </video>
            </div>
        `;
    } else if (turn.video_status === 'generating') {
        videoHtml = `
            <div class="video-generating">
                <div class="spinner"></div>
                <span>🎥 Video generating... (11s - 6min)</span>
            </div>
        `;
    } else if (turn.video_status === 'error') {
        videoHtml = `
            <div class="video-error">
                ⚠️ Video generation failed
            </div>
        `;
    }

    message.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">${emoji}</div>
            <div class="message-name">${turn.character_name}</div>
            <span class="message-model ${modelClass}">${modelLabel}</span>
            <div class="message-dials">${dialInfo}</div>
        </div>
        <div class="message-text">${turn.text}</div>
        ${videoHtml}
    `;

    feed.appendChild(message);
    feed.scrollTop = feed.scrollHeight;
}

// Test all 3 models with same prompt and dials
async function testAllModels() {
    if (isRunning) {
        alert('Stop the conversation first');
        return;
    }

    // Pick a random character
    const character = characters[Math.floor(Math.random() * characters.length)];
    
    showStatus(`Testing all 3 models with ${character.character_name}...`, 'info');
    
    const models = ['gpt-4', 'claude', 'gemini'];
    const context = `Share your thoughts on ${document.getElementById('topic-input').value}`;
    
    // Generate responses from all 3 models
    for (const model of models) {
        try {
            showStatus(`Generating ${model} response...`, 'info');
            
            const response = await fetch(`${API_URL}/api/conversation/turn`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    character_id: character.character_id,
                    context: context,
                    generate_video: false,  // Videos off for quick testing
                    model: model
                })
            });

            if (response.ok) {
                const data = await response.json();
                addMessage(data.turn);
            } else {
                console.error(`Failed to generate ${model} response`);
            }
            
            // Small delay between models
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (error) {
            console.error(`Error with ${model}:`, error);
        }
    }
    
    showStatus('All 3 models tested! Compare the responses above.', 'success');
}

// Clear conversation
async function clearConversation() {
    try {
        await fetch(`${API_URL}/api/conversation/history`, {
            method: 'DELETE'
        });
        document.getElementById('conversation-feed').innerHTML = `
            <div class="loading">
                <p>Conversation cleared. Click Start to begin a new tea party! 🫖</p>
            </div>
        `;
        currentTurn = 0;
        updateTurnCount();
        showStatus('Conversation cleared', 'success');
    } catch (error) {
        console.error('Failed to clear:', error);
    }
}

// WebSocket connection for real-time updates
function connectWebSocket() {
    try {
        ws = new WebSocket('ws://localhost:8000/ws/tea-party');

        ws.onopen = () => {
            console.log('WebSocket connected');
            showStatus('Connected', 'success');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'turn_generated') {
                addMessage(data.turn);
            } else if (data.type === 'dial_updated') {
                console.log('Dial updated:', data);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            showStatus('Connection error', 'error');
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            showStatus('Disconnected - using REST API', 'warning');
        };
    } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        showStatus('Using REST API only', 'warning');
    }
}

// Update turn counter
function updateTurnCount() {
    document.getElementById('turn-count').textContent = `Turn: ${currentTurn}/${maxTurns}`;
}

// Show status message
function showStatus(message, type = 'info') {
    const statusText = document.getElementById('status-text');
    statusText.textContent = message;
    
    // Could add color coding based on type
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Helper functions
function formatDimensionName(dimension) {
    const names = {
        'theory_of_mind': '🧠 Empathy',
        'harmfulness': '⚠️ Harm',
        'irony': '😏 Irony',
        'self_other': '👤 Self/Other'
    };
    return names[dimension] || dimension;
}

function getCharacterName(characterId) {
    const char = characters.find(c => c.character_id === characterId);
    return char ? char.character_name : characterId;
}

// Initialize when page loads
window.addEventListener('DOMContentLoaded', init);
