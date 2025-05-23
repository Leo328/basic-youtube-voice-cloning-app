<!-- Main application component -->
<script lang="ts">
  import { onDestroy } from 'svelte';

  // API configuration
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  console.log('API Base URL:', API_BASE_URL); // For debugging
  
  let youtubeUrl: string = '';
  let voiceName: string = '';
  let voices: Record<string, string> = {};
  let loading: boolean = false;
  let extractingAudio: boolean = false;
  let error: string | null = null;
  let currentVoiceId: string | null = null;
  let inputText: string = '';
  let selectedVoice: string | null = null;
  let currentStatus: string = '';
  let isProcessing = false;
  let eventSource: EventSource | null = null;
  let retryCount = 0;
  const MAX_RETRIES = 3;

  // Function to update status with proper capitalization
  function updateStatus(message: string) {
    // Ensure first letter is capitalized
    currentStatus = message.charAt(0).toUpperCase() + message.slice(1);
  }

  // Function to setup SSE connection with retry logic
  function setupProgressUpdates() {
    if (eventSource) {
      eventSource.close();
    }
    
    if (retryCount >= MAX_RETRIES) {
      console.error('Max retries reached for SSE connection');
      return;
    }
    
    eventSource = new EventSource(`${API_BASE_URL}/progress-updates`);
    
    eventSource.addEventListener('progress', (event: MessageEvent) => {
      console.log('Progress update received:', event.data);
      updateStatus(event.data);
    });
    
    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      if (eventSource) {
        eventSource.close();
        eventSource = null;
        
        // Retry connection after a delay
        setTimeout(() => {
          retryCount++;
          setupProgressUpdates();
        }, 1000);
      }
    };
    
    eventSource.onopen = () => {
      console.log('SSE connection established');
      retryCount = 0; // Reset retry count on successful connection
    };
  }

  async function handleYouTubeSubmit() {
    if (!youtubeUrl) {
      error = "Please enter a YouTube URL";
      return;
    }
    
    error = null;
    isProcessing = true;
    retryCount = 0; // Reset retry count before starting
    updateStatus("Starting voice cloning process...");
    
    try {
      // Setup SSE connection before starting the process
      setupProgressUpdates();
      
      // Extract audio from YouTube
      const extractResponse = await fetch(`${API_BASE_URL}/extract-audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: youtubeUrl })
      });
      
      if (!extractResponse.ok) {
        const errorData = await extractResponse.json();
        throw new Error(errorData.detail || 'Failed to extract audio');
      }
      
      const extractData = await extractResponse.json();
      
      if (!extractData.file_path) {
        throw new Error('No audio file path returned from extraction');
      }
      
      // Clone the voice
      updateStatus("Creating voice clone with ElevenLabs...");
      const cloneResponse = await fetch(`${API_BASE_URL}/clone-voice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio_file: extractData.file_path })
      });
      
      if (!cloneResponse.ok) {
        const errorData = await cloneResponse.json();
        throw new Error(errorData.detail || 'Failed to clone voice');
      }
      
      const cloneData = await cloneResponse.json();
      updateStatus("Voice clone created successfully!");
      
      // Show the save dialog
      currentVoiceId = cloneData.voice_id;
      
    } catch (e) {
      error = e.message;
      updateStatus(`Error: ${e.message}`);
    } finally {
      isProcessing = false;
      if (eventSource) {
        eventSource.close();
        eventSource = null;
      }
    }
  }

  async function saveVoice() {
    if (!currentVoiceId || !voiceName) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/save-voice?voice_id=${currentVoiceId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: voiceName })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save voice');
      }
      
      await loadVoices();
      voiceName = '';
      currentVoiceId = null;
      currentStatus = '';
    } catch (e) {
      error = e.message;
    }
  }

  async function loadVoices() {
    try {
      const response = await fetch(`${API_BASE_URL}/voices`).catch(() => {
        // Silently handle network errors during initial load
        return { ok: false, json: async () => ({}) } as Response;
      });
      
      if (!response.ok) {
        // Don't show error for network issues
        voices = {};
        return;
      }
      
      voices = await response.json();
      // Clear any previous errors if load was successful
      error = null;
    } catch (e) {
      // Only show errors that aren't network-related
      if (!(e instanceof TypeError && e.message === 'Failed to fetch')) {
        error = e.message;
      }
      voices = {};
    }
  }

  async function playQuestion(voiceId: string) {
    try {
      // Find the name associated with this voice ID
      const voiceName = Object.entries(voices).find(([name, id]) => id === voiceId)?.[0];
      if (!voiceName) throw new Error('Voice name not found');

      const response = await fetch(`${API_BASE_URL}/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voice_name: voiceName,
          text: `What would you like me to say? My name is ${voiceName}.`
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate speech');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      await audio.play();
    } catch (e) {
      error = e.message;
    }
  }

  async function playCustomText() {
    if (!selectedVoice || !inputText) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voice_name: selectedVoice,
          text: inputText
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate speech');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      await audio.play();
    } catch (e) {
      error = e.message;
    }
  }

  async function deleteVoice(name: string) {
    if (!confirm(`Are you sure you want to delete the voice "${name}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/voices/${encodeURIComponent(name)}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete voice');
      }
      
      await loadVoices();
    } catch (e) {
      error = e.message;
    }
  }

  // Load voices when component mounts
  loadVoices();

  // Clean up EventSource on component unmount
  onDestroy(() => {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  });
</script>

<main class="container">
  <h1>YouTube Voice Cloning App</h1>
  
  {#if error}
    <div class="error">
      {error}
    </div>
  {/if}

  <div class="youtube-section">
    <h2>Clone Voice from YouTube</h2>
    <h3>Select a YouTube video to clone the voice from, ideally less than 6 minutes as ElevenLabs has an 11mb file limit</h3>
    <div class="input-group">
      <input
        type="text"
        bind:value={youtubeUrl}
        placeholder="Enter YouTube URL"
        disabled={isProcessing}
      />
      <button on:click={handleYouTubeSubmit} disabled={isProcessing}>
        {#if isProcessing}
          <div class="spinner"></div>
          Processing...
        {:else}
          Clone Voice
        {/if}
      </button>
    </div>
    
    {#if currentStatus}
      <div class="status-container" 
           class:error={currentStatus.startsWith('Error')} 
           class:success={currentStatus.includes('success')}
           class:processing={isProcessing && !currentStatus.startsWith('Error')}>
        <div class="status-message">
          {#if isProcessing && !currentStatus.startsWith('Error')}
            <div class="status-spinner"></div>
          {/if}
          {currentStatus}
        </div>
      </div>
    {/if}
  </div>

  {#if currentVoiceId}
    <div class="voice-naming">
      <h2>Name this voice</h2>
      <div class="input-group">
        <input
          type="text"
          bind:value={voiceName}
          placeholder="Enter a name for this voice"
        />
        <button on:click={saveVoice} disabled={!voiceName}>
          Save Voice
        </button>
      </div>
    </div>
  {/if}

  {#if Object.keys(voices).length > 0}
    <div class="voice-list">
      <h2>Saved Voices</h2>
      <ul>
        {#each Object.entries(voices) as [name, id]}
          <li>
            <span>{name}</span>
            <div class="button-group">
              <button on:click={() => playQuestion(id)}>
                Play Sample
              </button>
              <button class="delete-button" on:click={() => deleteVoice(name)}>
                Delete
              </button>
            </div>
          </li>
        {/each}
      </ul>
    </div>

    <div class="custom-text">
      <h2>Generate Custom Speech</h2>
      <div class="input-group">
        <select bind:value={selectedVoice}>
          <option value="">Select a voice</option>
          {#each Object.keys(voices) as name}
            <option value={name}>{name}</option>
          {/each}
        </select>
        <textarea
          bind:value={inputText}
          placeholder="Enter text to speak..."
          rows="3"
        ></textarea>
        <button on:click={playCustomText} disabled={!selectedVoice || !inputText}>
          Speak Text
        </button>
      </div>
    </div>
  {/if}
</main>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    background-color: #ffffff;
  }

  h1 {
    color: #333333;
    text-align: center;
    margin-bottom: 2rem;
  }

  .error {
    background-color: #ff6b6b;
    color: white;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .youtube-section {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 4px;
    margin-bottom: 2rem;
  }

  .youtube-section h2 {
    color: #2c3e50;
    margin-bottom: 0.5rem;
  }

  .youtube-section h3 {
    color: #34495e;
    font-size: 1rem;
    margin-bottom: 1.5rem;
    font-weight: normal;
  }

  .input-group {
    display: flex;
    gap: 1rem;
  }

  input {
    flex: 1;
    padding: 0.5rem;
    border: 2px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  button {
    padding: 0.5rem 1rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  button:disabled {
    background-color: #bdc3c7;
    cursor: not-allowed;
  }

  .voice-naming {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 4px;
    margin-bottom: 2rem;
  }

  .voice-list {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 4px;
  }

  .voice-list ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .voice-list li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #ddd;
  }

  .voice-list li:last-child {
    border-bottom: none;
  }

  .custom-text {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 4px;
    margin-top: 2rem;
  }

  textarea {
    width: 100%;
    padding: 0.5rem;
    border: 2px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    margin: 1rem 0;
    resize: vertical;
  }

  select {
    width: 100%;
    padding: 0.5rem;
    border: 2px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }

  .custom-text .input-group {
    display: flex;
    flex-direction: column;
  }

  .custom-text button {
    align-self: flex-end;
  }

  .button-group {
    display: flex;
    gap: 0.5rem;
  }

  .delete-button {
    background-color: #e74c3c;
  }

  .delete-button:hover {
    background-color: #c0392b;
  }

  .status-container {
    margin: 20px 0;
    padding: 15px;
    border-radius: 8px;
    background: #f8f9fa;
    border-left: 4px solid #3498db;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
  }

  .status-container.processing {
    background: #f0f7ff;
    border-left-color: #3498db;
  }

  .status-container.error {
    background: #fff5f5;
    border-left-color: #e74c3c;
  }

  .status-container.success {
    background: #f0fff4;
    border-left-color: #2ecc71;
  }

  .status-message {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1rem;
    color: #2c3e50;
  }

  .status-spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .status-container.error .status-message {
    color: #c0392b;
  }

  .status-container.success .status-message {
    color: #27ae60;
  }

  .status-container.processing .status-message {
    color: #2980b9;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>
