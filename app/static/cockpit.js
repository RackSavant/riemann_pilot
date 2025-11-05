// Tea Party Cockpit Control System
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

// Dimension display names
const dimensionNames = {
    'theory_of_mind': '🧠 EMPATHY',
    'harmfulness': '⚠️ HARM',
    'irony': '😏 IRONY',
    'self_other': '👤 FOCUS'
};

// Initialize cockpit systems
async function init() {
    showLoading(true);
    await loadCharacters();
    renderInstrumentPanels();
    setupEventListeners();
    connectWebSocket();
    showLoading(false);
}

// Show/hide loading overlay
function showLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

// Load characters from API
async function loadCharacters() {
    try {
        console.log('Fetching characters from:', `${API_URL}/api/characters`);
        const response = await fetch(`${API_URL}/api/characters`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Characters loaded:', data.count);
        characters = data.characters;
    } catch (error) {
        console.error('Failed to load characters:', error);
        console.error('Error details:', error.message, error.stack);
        updateStatus('ERROR: SYSTEM OFFLINE', 'error');
    }
}

// Render instrument panels for each character
function renderInstrumentPanels() {
    const container = document.getElementById('dashboard-grid');
    if (!container) {
        console.error('dashboard-grid element not found!');
        return;
    }
    container.innerHTML = '';

    console.log(`Rendering ${characters.length} character panels...`);
    characters.forEach(char => {
        const panel = document.createElement('div');
        panel.className = 'instrument-panel';
        panel.id = `panel-${char.character_id}`;

        const emoji = characterEmojis[char.character_id] || '👤';

        let dialsHtml = '';
        console.log(`${char.character_name} dial_values:`, char.dial_values);
        for (const [dimension, value] of Object.entries(char.dial_values)) {
            const percentage = Math.round(value * 100);
            const angle = -90 + (value * 180); // -90 to +90 degrees
            console.log(`  Creating dial: ${dimension} = ${percentage}%`);
            
            dialsHtml += `
                <div class="dial-gauge">
                    <div class="gauge-label">
                        <span>${dimensionNames[dimension] || dimension}</span>
                        <span class="gauge-value" id="${char.character_id}-${dimension}-value">${percentage}%</span>
                    </div>
                    <div class="gauge-visual">
                        <div class="gauge-bg"></div>
                        <div class="gauge-fill" id="${char.character_id}-${dimension}-needle" 
                             style="transform: rotate(${angle}deg)"></div>
                    </div>
                    <input 
                        type="range" 
                        class="dial-slider" 
                        min="0" 
                        max="100" 
                        value="${percentage}"
                        data-character="${char.character_id}"
                        data-dimension="${dimension}"
                    >
                </div>
            `;
        }

        panel.innerHTML = `
            <div class="instrument-header">
                <div style="font-size: 2em; margin-bottom: 8px;">${emoji}</div>
                <div class="character-name">${char.character_name}</div>
                <div class="character-id">${char.character_id.replace('_', '-')}</div>
            </div>
            ${dialsHtml}
        `;

        container.appendChild(panel);
    });

    // Add slider event listeners
    document.querySelectorAll('.dial-slider').forEach(slider => {
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

    // Update gauge needle
    const angle = -90 + (value * 180);
    const needle = document.getElementById(`${characterId}-${dimension}-needle`);
    if (needle) {
        needle.style.transform = `rotate(${angle}deg)`;
    }

    // Highlight active panel
    document.querySelectorAll('.instrument-panel').forEach(panel => {
        panel.style.borderColor = '#444';
    });
    document.getElementById(`panel-${characterId}`).style.borderColor = '#00ff00';
    document.getElementById(`panel-${characterId}`).style.boxShadow = '0 0 20px rgba(0,255,0,0.3)';

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
            updateStatus(`${dimensionNames[dimension]} adjusted`, 'success');
            // Reset panel highlight after delay
            setTimeout(() => {
                document.getElementById(`panel-${characterId}`).style.borderColor = '#444';
                document.getElementById(`panel-${characterId}`).style.boxShadow = 'inset 0 2px 10px rgba(0,0,0,0.5)';
            }, 1000);
        }
    } catch (error) {
        console.error('Failed to update dial:', error);
        updateStatus('ERROR: DIAL UPDATE FAILED', 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('test-prompt-btn').addEventListener('click', testPromptWithAllAvatars);
    document.getElementById('start-btn').addEventListener('click', startConversation);
    document.getElementById('stop-btn').addEventListener('click', stopConversation);
    document.getElementById('clear-btn').addEventListener('click', clearConversation);
}

// Start auto-play conversation
async function startConversation() {
    if (isRunning) return;

    isRunning = true;
    currentTurn = 0;
    document.getElementById('start-btn').style.display = 'none';
    document.getElementById('stop-btn').style.display = 'inline-block';

    const topic = document.getElementById('prompt-input').value || 'tea and pastries';
    updateStatus(`FLIGHT INITIATED: ${topic.toUpperCase()}`, 'info');

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
    updateStatus('FLIGHT ABORTED', 'warning');
}

// Auto-play loop
async function runAutoPlay() {
    if (!isRunning || currentTurn >= maxTurns) {
        stopConversation();
        updateStatus('MISSION COMPLETE', 'success');
        return;
    }

    const characterIndex = currentTurn % characters.length;
    const character = characters[characterIndex];
    const model = document.getElementById('model-select').value;
    const generateVideo = document.getElementById('video-toggle').checked;

    // Highlight active panel
    document.querySelectorAll('.instrument-panel').forEach(panel => {
        panel.style.borderColor = '#444';
        panel.style.boxShadow = 'inset 0 2px 10px rgba(0,0,0,0.5)';
    });
    const activePanel = document.getElementById(`panel-${character.character_id}`);
    if (activePanel) {
        activePanel.style.borderColor = '#00ff00';
        activePanel.style.boxShadow = '0 0 30px rgba(0,255,0,0.5)';
    }

    const statusMsg = generateVideo 
        ? `${character.character_name.toUpperCase()} TRANSMITTING + VEO`
        : `${character.character_name.toUpperCase()} TRANSMITTING`;
    updateStatus(statusMsg, 'speaking');

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

            // Reset panel highlight
            if (activePanel) {
                activePanel.style.borderColor = '#444';
                activePanel.style.boxShadow = 'inset 0 2px 10px rgba(0,0,0,0.5)';
            }

            autoPlayInterval = setTimeout(runAutoPlay, 2000);
        } else {
            throw new Error('Failed to generate response');
        }
    } catch (error) {
        console.error('Error generating turn:', error);
        updateStatus('ERROR: TRANSMISSION FAILED', 'error');
        stopConversation();
    }
}

// Add message to tea party view
function addMessage(turn) {
    const view = document.getElementById('tea-party-view');
    
    // Remove welcome message if present
    if (view.querySelector('h1') || view.querySelector('h2')) {
        view.innerHTML = '';
    }

    const message = document.createElement('div');
    message.className = 'conversation-message';

    const emoji = characterEmojis[turn.character_id] || '👤';
    const modelName = turn.model || 'gpt-4';
    const modelClass = `model-${modelName}`;
    const modelLabel = {
        'gpt-4': '🤖 GPT-4',
        'claude': '🧠 Claude',
        'gemini': '✨ Gemini'
    }[modelName] || modelName;

    let videoHtml = '';
    if (turn.video_url) {
        videoHtml = `
            <div class="msg-video">
                <video controls>
                    <source src="${turn.video_url}" type="video/mp4">
                </video>
            </div>
        `;
    } else if (turn.video_status === 'generating') {
        videoHtml = `
            <div style="padding: 12px; background: #fef3c7; border-radius: 8px; margin-top: 10px; color: #92400e;">
                <div class="spinner" style="width: 20px; height: 20px; margin: 0 auto 10px;"></div>
                🎥 Video generating... (11s - 6min)
            </div>
        `;
    }

    message.innerHTML = `
        <div class="msg-header">
            <div class="msg-avatar">${emoji}</div>
            <div class="msg-name">${turn.character_name}</div>
            <span class="msg-model ${modelClass}">${modelLabel}</span>
        </div>
        <div class="msg-text">${turn.text}</div>
        ${videoHtml}
    `;

    view.appendChild(message);
    view.scrollTop = view.scrollHeight;
}

// Add response as a column in the grid
function addResponseColumn(turn, responseNumber, gridContainer) {
    const column = document.createElement('div');
    column.className = 'response-column';

    const emoji = characterEmojis[turn.character_id] || '👤';
    const modelName = turn.model || 'gpt-4';
    const modelClass = `model-${modelName}`;
    const modelLabel = {
        'gpt-4': '🤖 GPT-4',
        'claude': '🧠 Claude',
        'gemini': '✨ Gemini'
    }[modelName] || modelName;

    // Format dial values
    const dialInfo = Object.entries(turn.dial_values)
        .map(([key, val]) => `${key.replace('_', ' ')}: ${Math.round(val * 100)}%`)
        .join(' | ');

    // Generate validation scores (will be real from API later)
    const validationHtml = generateValidationScoresHtml(turn);

    let videoHtml = '';
    if (turn.video_url) {
        videoHtml = `
            <div class="msg-video">
                <video controls>
                    <source src="${turn.video_url}" type="video/mp4">
                </video>
            </div>
        `;
    } else if (turn.video_status === 'generating') {
        videoHtml = `
            <div style="padding: 12px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 8px; margin-top: 10px; color: white; text-align: center;">
                <div class="spinner" style="width: 24px; height: 24px; border: 3px solid rgba(255,255,255,0.3); border-top: 3px solid white; border-radius: 50%; margin: 0 auto 8px; animation: spin 1s linear infinite;"></div>
                <strong>� VEO Generating Video...</strong>
                <div style="font-size: 0.85em; margin-top: 4px; opacity: 0.9;">Est. 30 seconds - 6 minutes</div>
            </div>
        `;
    }

    column.innerHTML = `
        <div class="response-number">
            ${responseNumber}. ${turn.character_name.toUpperCase()}
        </div>
        <div class="msg-header">
            <div class="msg-avatar">${emoji}</div>
            <div class="msg-name">${turn.character_name}</div>
            <span class="msg-model ${modelClass}">${modelLabel}</span>
        </div>
        <div style="font-size: 0.8em; color: #888; padding: 8px 0; border-bottom: 1px solid #eee; margin-bottom: 10px;">
            ${dialInfo}
        </div>
        <div class="msg-text">${turn.text}</div>
        ${validationHtml}
        ${videoHtml}
    `;

    gridContainer.appendChild(column);
}

// Add message with validation scores (for non-grid display)
function addMessageWithValidation(turn, responseNumber) {
    const view = document.getElementById('tea-party-view');
    
    // Remove welcome message if present
    if (view.querySelector('h1') || view.querySelector('h2')) {
        view.innerHTML = '';
    }

    const message = document.createElement('div');
    message.className = 'conversation-message';

    const emoji = characterEmojis[turn.character_id] || '👤';
    const modelName = turn.model || 'gpt-4';
    const modelClass = `model-${modelName}`;
    const modelLabel = {
        'gpt-4': '🤖 GPT-4',
        'claude': '🧠 Claude',
        'gemini': '✨ Gemini'
    }[modelName] || modelName;

    // Format dial values
    const dialInfo = Object.entries(turn.dial_values)
        .map(([key, val]) => `${key.replace('_', ' ')}: ${Math.round(val * 100)}%`)
        .join(' | ');

    // Generate validation scores
    const validationHtml = generateValidationScoresHtml(turn);

    let videoHtml = '';
    if (turn.video_url) {
        videoHtml = `
            <div class="msg-video">
                <video controls>
                    <source src="${turn.video_url}" type="video/mp4">
                </video>
            </div>
        `;
    } else if (turn.video_status === 'generating') {
        videoHtml = `
            <div style="padding: 12px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 8px; margin-top: 10px; color: white; text-align: center;">
                <div class="spinner" style="width: 24px; height: 24px; border: 3px solid rgba(255,255,255,0.3); border-top: 3px solid white; border-radius: 50%; margin: 0 auto 8px; animation: spin 1s linear infinite;"></div>
                <strong>� VEO Generating Video...</strong>
                <div style="font-size: 0.85em; margin-top: 4px; opacity: 0.9;">Est. 30 seconds - 6 minutes</div>
            </div>
        `;
    }

    message.innerHTML = `
        <div style="background: #f0f0f0; padding: 8px 12px; border-radius: 8px 8px 0 0; font-weight: bold; color: #666;">
            Response ${responseNumber} of 5
        </div>
        <div class="msg-header">
            <div class="msg-avatar">${emoji}</div>
            <div class="msg-name">${turn.character_name}</div>
            <span class="msg-model ${modelClass}">${modelLabel}</span>
        </div>
        <div style="font-size: 0.85em; color: #888; padding: 8px 0; border-bottom: 1px solid #eee;">
            ${dialInfo}
        </div>
        <div class="msg-text">${turn.text}</div>
        ${validationHtml}
        ${videoHtml}
    `;

    view.appendChild(message);
    view.scrollTop = view.scrollHeight;
}

// Generate validation scores HTML
function generateValidationScoresHtml(turn) {
    const scores = turn.validation_scores || {};
    
    // If no validation scores, show dial values only
    if (Object.keys(scores).length === 0) {
        const dialScores = [];
        for (const [dimension, value] of Object.entries(turn.dial_values)) {
            const percentage = Math.round(value * 100);
            const label = {
                'theory_of_mind': '🧠 Empathy',
                'harmfulness': '⚠️ Harm',
                'irony': '😏 Irony',
                'self_other': '👤 Focus'
            }[dimension] || dimension;
            
            dialScores.push(`
                <div class="validation-score">
                    <span class="validation-label">${label} Setting:</span>
                    <span class="validation-value score-good">${percentage}%</span>
                </div>
            `);
        }
        
        return `
            <div class="msg-validation">
                <strong>📊 Current Dial Settings:</strong>
                ${dialScores.join('')}
                <div style="margin-top: 10px; padding: 8px; background: #fef3c7; border-radius: 4px; font-size: 0.9em;">
                    <strong>Note:</strong> Response generated with above settings. 
                    <em>Semantic validation loading...</em>
                </div>
            </div>
        `;
    }
    
    // WITH REAL VALIDATION SCORES from semantic similarity
    console.log('📊 Validation scores received:', scores);
    
    const validationRows = [];
    for (const [dimension, data] of Object.entries(scores)) {
        if (typeof data === 'object' && data.alignment) {
            const alignmentPercent = Math.round(data.alignment * 100);
            const scoreClass = getScoreClass(alignmentPercent);
            const badge = alignmentPercent >= 70 ? 'effective' : alignmentPercent >= 50 ? 'partial' : 'ineffective';
            const badgeText = alignmentPercent >= 70 ? '✅ EFFECTIVE' : alignmentPercent >= 50 ? '⚠️ PARTIAL' : '❌ WEAK';
            
            const label = {
                'theory_of_mind': '🧠 Empathy',
                'harmfulness': '⚠️ Harm',
                'irony': '😏 Irony',
                'self_other': '👤 Focus'
            }[dimension] || dimension;
            
            validationRows.push(`
                <div class="validation-score">
                    <span class="validation-label">${label} Alignment:</span>
                    <span class="validation-value score-${scoreClass}">
                        ${alignmentPercent}%
                        <span class="validation-badge badge-${badge}">${badgeText}</span>
                    </span>
                </div>
                <div style="font-size: 0.8em; color: #666; margin-left: 20px; margin-top: -3px; margin-bottom: 8px;">
                    Dial: ${Math.round(data.dial_value * 100)}% | 
                    Low Sim: ${data.low_similarity.toFixed(2)} | 
                    High Sim: ${data.high_similarity.toFixed(2)}
                </div>
            `);
        }
    }
    
    // Overall effectiveness
    const hasOverall = scores.overall_similarity !== undefined;
    const overallHtml = hasOverall ? `
        <div style="margin-top: 12px; padding: 10px; background: #dcfce7; border-radius: 5px; font-weight: bold; color: #16a34a;">
            📈 Overall Similarity: ${(scores.overall_similarity * 100).toFixed(1)}%
            ${scores.candidates_tested ? ` | Tested ${scores.candidates_tested} candidates` : ''}
        </div>
    ` : '';
    
    return `
        <div class="msg-validation">
            <strong>✅ Semantic Validation (Proof Steering Works):</strong>
            ${validationRows.join('')}
            ${overallHtml}
            <div style="margin-top: 8px; font-size: 0.85em; color: #555; font-style: italic;">
                Alignment >70% = Effective | 50-70% = Partial | <50% = Needs tuning
            </div>
        </div>
    `;
}

function getScoreClass(score) {
    if (score >= 85) return 'excellent';
    if (score >= 70) return 'good';
    if (score >= 50) return 'fair';
    return 'poor';
}

// TEST PROMPT - Generate responses from all 5 avatars with current dial settings
async function testPromptWithAllAvatars() {
    if (isRunning) {
        alert('ABORT FLIGHT FIRST');
        return;
    }

    const prompt = document.getElementById('prompt-input').value.trim();
    if (!prompt) {
        alert('ENTER A PROMPT FIRST');
        return;
    }

    const model = document.getElementById('model-select').value;
    const generateVideo = document.getElementById('video-toggle').checked;

    updateStatus(`TESTING PROMPT WITH ALL 5 AVATARS...`, 'info');
    console.log(`\n🔬 TESTING PROMPT: "${prompt}"`);
    console.log(`Model: ${model}, Video: ${generateVideo}\n`);

    // Clear previous results and create grid
    const view = document.getElementById('tea-party-view');
    view.innerHTML = `
        <div style="text-align: center; padding: 20px; color: white;">
            <h2>🫖 TEA PARTY FOR 5</h2>
            <p>Steering, Stirring, and Sipping responses with current dial settings...</p>
        </div>
        <div id="response-grid" class="response-grid"></div>
    `;
    
    const responseGrid = document.getElementById('response-grid');

    // Test each character
    for (let i = 0; i < characters.length; i++) {
        const character = characters[i];
        
        // Highlight active character panel
        document.querySelectorAll('.instrument-panel').forEach(panel => {
            panel.style.borderColor = '#444';
            panel.style.boxShadow = 'inset 0 2px 10px rgba(0,0,0,0.5)';
        });
        const activePanel = document.getElementById(`panel-${character.character_id}`);
        if (activePanel) {
            activePanel.style.borderColor = '#00ff00';
            activePanel.style.boxShadow = '0 0 30px rgba(0,255,0,0.5)';
        }

        updateStatus(`${character.character_name.toUpperCase()} RESPONDING...`, 'speaking');
        console.log(`\n📡 Generating response for ${character.character_name}...`);
        console.log(`  Dial values:`, character.dial_values);

        try {
            const response = await fetch(`${API_URL}/api/conversation/turn`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    character_id: character.character_id,
                    context: prompt,
                    generate_video: generateVideo,
                    model: model
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log(`  ✅ Response received:`, data.turn.text.substring(0, 100) + '...');
                
                // Add response as column in grid
                addResponseColumn(data.turn, i + 1, responseGrid);
            } else {
                console.error(`  ❌ Failed:`, response.status, response.statusText);
                throw new Error(`HTTP ${response.status}`);
            }

            // Reset panel highlight
            if (activePanel) {
                activePanel.style.borderColor = '#444';
                activePanel.style.boxShadow = 'inset 0 2px 10px rgba(0,0,0,0.5)';
            }

            // Delay between characters to avoid rate limits (free model = 16/min)
            await new Promise(resolve => setTimeout(resolve, 5000));  // 5 seconds = safe for free tier

        } catch (error) {
            console.error(`Error with ${character.character_name}:`, error);
            updateStatus(`ERROR: ${character.character_name.toUpperCase()} FAILED`, 'error');
        }
    }

    updateStatus('ALL 5 AVATARS RESPONDED - COMPARE RESULTS', 'success');
    console.log('\n✅ Test complete! All 5 responses generated.\n');
    
    // Show Tea Party Scene Video button
    showTeaPartyVideoButton();
}

// Global variable to store current responses for video generation
let currentResponses = [];

// Show the Tea Party Scene Video button
function showTeaPartyVideoButton() {
    const view = document.getElementById('tea-party-view');
    
    // Check if button already exists
    if (document.getElementById('scene-video-actions')) {
        return;
    }
    
    // Store responses for video generation
    currentResponses = [];
    const responseColumns = document.querySelectorAll('.response-column');
    responseColumns.forEach((column, index) => {
        const character = characters[index];
        const text = column.querySelector('.msg-text').textContent;
        currentResponses.push({
            character_id: character.character_id,
            character_name: character.character_name,
            text: text
        });
    });
    
    const sceneVideoActions = document.createElement('div');
    sceneVideoActions.id = 'scene-video-actions';
    sceneVideoActions.className = 'video-actions';
    sceneVideoActions.innerHTML = `
        <button id="generate-scene-btn" class="generate-videos-btn" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            🎬 GENERATE TEA PARTY SCENE VIDEO
        </button>
        <div style="font-size: 0.9em; color: #ccc; margin-top: 8px; text-align: center;">
            Create one video showing all 5 characters conversing together
        </div>
        <div id="scene-video-status" class="video-status" style="display: none;"></div>
        <div id="scene-video-player" style="margin-top: 20px; display: none;">
            <h3 style="text-align: center; color: white;">🫖 Tea Party Conversation</h3>
            <video id="scene-video" controls style="width: 100%; max-width: 800px; margin: 0 auto; display: block; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
            </video>
        </div>
    `;
    
    view.appendChild(sceneVideoActions);
    
    // Add click handler
    document.getElementById('generate-scene-btn').addEventListener('click', generateTeaPartySceneVideo);
}

// Generate Tea Party Scene Video
async function generateTeaPartySceneVideo() {
    const btn = document.getElementById('generate-scene-btn');
    const status = document.getElementById('scene-video-status');
    const playerContainer = document.getElementById('scene-video-player');
    
    btn.disabled = true;
    status.style.display = 'block';
    playerContainer.style.display = 'none';
    
    status.innerHTML = `
        <div style="padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 8px; color: white; text-align: center;">
            <div class="spinner" style="width: 32px; height: 32px; border: 4px solid rgba(255,255,255,0.3); border-top: 4px solid white; border-radius: 50%; margin: 0 auto 12px; animation: spin 1s linear infinite;"></div>
            <strong>🎬 Generating Tea Party Scene Video...</strong>
            <div style="font-size: 0.9em; margin-top: 8px; opacity: 0.9;">Creating 30-second conversation with all 5 characters</div>
            <div style="font-size: 0.85em; margin-top: 4px; opacity: 0.8;">This may take 1-10 minutes...</div>
        </div>
    `;
    
    console.log('\n🎬 Starting Tea Party Scene Video generation...');
    console.log('  Responses:', currentResponses.length);
    
    try {
        // Call backend to generate conversation video
        const response = await fetch(`${API_URL}/api/video/conversation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                responses: currentResponses
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Scene video generation response:', data);
        
        if (data.video_url) {
            // Success! Show video player
            const videoPlayer = document.getElementById('scene-video');
            videoPlayer.src = data.video_url;
            
            playerContainer.style.display = 'block';
            status.innerHTML = `
                <div style="padding: 16px; background: linear-gradient(135deg, #11998e, #38ef7d); border-radius: 8px; color: white; text-align: center;">
                    <strong>✅ Tea Party Scene Video Complete!</strong>
                    <div style="font-size: 0.9em; margin-top: 4px;">Watch all 5 characters conversing together below ↓</div>
                </div>
            `;
            
            // Scroll to video
            playerContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            btn.textContent = '🎬 REGENERATE SCENE VIDEO';
            btn.disabled = false;
            
            console.log('✅ Scene video ready!');
        } else if (data.status === 'generating') {
            status.innerHTML = `
                <div style="padding: 16px; background: #fbbf24; border-radius: 8px; color: #78350f; text-align: center;">
                    <strong>⏳ Video is processing...</strong>
                    <div style="font-size: 0.9em; margin-top: 4px;">Operation: ${data.operation_name}</div>
                </div>
            `;
            btn.disabled = false;
        }
        
    } catch (error) {
        console.error('❌ Scene video generation failed:', error);
        status.innerHTML = `
            <div style="padding: 16px; background: #ef4444; border-radius: 8px; color: white; text-align: center;">
                <strong>❌ Video Generation Failed</strong>
                <div style="font-size: 0.9em; margin-top: 4px;">${error.message}</div>
                <div style="font-size: 0.85em; margin-top: 8px; opacity: 0.9;">Make sure VEO API access is enabled and reference image exists</div>
            </div>
        `;
        btn.disabled = false;
    }
}

// Show the Generate Videos button after text responses
function showGenerateVideosButton() {
    const view = document.getElementById('tea-party-view');
    
    // Check if button already exists
    if (document.getElementById('video-actions')) {
        return;
    }
    
    const videoActions = document.createElement('div');
    videoActions.id = 'video-actions';
    videoActions.className = 'video-actions';
    videoActions.innerHTML = `
        <button id="generate-videos-btn" class="generate-videos-btn">
            🎬 GENERATE VIDEOS (Test with 1 first)
        </button>
        <div id="video-status" class="video-status" style="display: none;"></div>
    `;
    
    view.appendChild(videoActions);
    
    // Add click handler
    document.getElementById('generate-videos-btn').addEventListener('click', generateVideosManually);
}

// Generate videos for responses (starting with just 1 for testing)
async function generateVideosManually() {
    const btn = document.getElementById('generate-videos-btn');
    const status = document.getElementById('video-status');
    
    btn.disabled = true;
    status.style.display = 'block';
    status.textContent = '🎬 Generating test video for first response...';
    
    console.log('\n🎬 Starting VEO video generation (TEST MODE - 1 video only)...');
    
    // Get all response columns
    const responseColumns = document.querySelectorAll('.response-column');
    
    if (responseColumns.length === 0) {
        status.textContent = '❌ No responses found to generate videos for';
        btn.disabled = false;
        return;
    }
    
    // TEST: Only generate video for FIRST response
    const firstColumn = responseColumns[0];
    const characterName = characters[0].character_name;
    const characterId = characters[0].character_id;
    const responseText = firstColumn.querySelector('.msg-text').textContent;
    
    console.log(`🎥 Generating video for ${characterName}...`);
    console.log(`   Text: ${responseText.substring(0, 100)}...`);
    
    status.textContent = `🎬 Generating video for ${characterName}... (This takes 30s-6min)`;
    
    try {
        // Call backend to generate video
        const response = await fetch(`${API_URL}/api/video/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                character_id: characterId,
                dialogue: responseText
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Video generation response:', data);
        
        if (data.video_url) {
            // Success! Add video to the first column
            const videoHtml = `
                <div class="msg-video" style="margin-top: 15px;">
                    <video controls style="width: 100%; border-radius: 8px;">
                        <source src="${data.video_url}" type="video/mp4">
                    </video>
                </div>
            `;
            firstColumn.querySelector('.msg-text').insertAdjacentHTML('afterend', videoHtml);
            
            status.textContent = `✅ Video generated successfully! Check ${characterName}'s response above.`;
            btn.textContent = '🎬 GENERATE ALL 5 VIDEOS';
            btn.disabled = false;
            
            console.log('✅ Video successfully added to UI!');
        } else if (data.status === 'generating') {
            status.textContent = `⏳ Video is processing... Operation: ${data.operation_name}`;
            // TODO: Add polling to check status
        }
        
    } catch (error) {
        console.error('❌ Video generation failed:', error);
        status.textContent = `❌ Video generation failed: ${error.message}`;
        btn.disabled = false;
    }
}

// Clear conversation
async function clearConversation() {
    try {
        await fetch(`${API_URL}/api/conversation/history`, {
            method: 'DELETE'
        });
        
        const view = document.getElementById('tea-party-view');
        view.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; color: white;">
                <h1 style="font-size: 2.5em; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">☕ TEA PARTY VIEW</h1>
                <p style="font-size: 1.2em; opacity: 0.9;">Adjust the instrument dials below to control the conversation sentiment</p>
                <p style="margin-top: 20px; opacity: 0.7;">Click START FLIGHT to begin the tea party</p>
            </div>
        `;
        
        currentTurn = 0;
        updateTurnCount();
        updateStatus('SYSTEMS RESET', 'success');
    } catch (error) {
        console.error('Failed to clear:', error);
        updateStatus('ERROR: RESET FAILED', 'error');
    }
}

// WebSocket connection
function connectWebSocket() {
    try {
        ws = new WebSocket('ws://localhost:8000/ws/tea-party');

        ws.onopen = () => {
            console.log('WebSocket connected');
            updateStatus('SYSTEMS ONLINE', 'success');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'turn_generated') {
                addMessage(data.turn);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateStatus('WARNING: WS OFFLINE', 'warning');
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            updateStatus('USING REST API', 'warning');
        };
    } catch (error) {
        console.error('Failed to connect WebSocket:', error);
    }
}

// Update turn counter
function updateTurnCount() {
    document.getElementById('turn-count').textContent = `${currentTurn}/${maxTurns}`;
}

// Update status display
function updateStatus(message, type = 'info') {
    const statusText = document.getElementById('status-text');
    statusText.textContent = message.toUpperCase();
    
    // Color coding
    const colors = {
        'success': '#00ff00',
        'error': '#ff0000',
        'warning': '#ffff00',
        'info': '#00ffff',
        'speaking': '#00ff00'
    };
    
    statusText.style.color = colors[type] || '#00ffff';
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Initialize when page loads
window.addEventListener('DOMContentLoaded', init);
