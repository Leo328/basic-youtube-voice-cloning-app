<!-- Main application component -->
<script lang="ts">
  let youtubeUrl: string = '';
  let voiceName: string = '';
  let voices: Record<string, string> = {};
  let loading: boolean = false;
  let extractingAudio: boolean = false;
  let error: string | null = null;
  let currentVoiceId: string | null = null;
  let inputText: string = '';
  let selectedVoice: string | null = null;
  let progressMessage: string = '';
  let progressUpdates: string[] = [];
  let isProcessing = false;

  async function handleYouTubeSubmit() {
    if (!youtubeUrl) {
      error = "Please enter a YouTube URL";
      return;
    }
    
    error = null;
    isProcessing = true;
    progressUpdates = ["Starting voice cloning process..."];
    
    try {
      // Extract audio from YouTube
      const extractResponse = await fetch('http://localhost:8000/extract-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: youtubeUrl })
      });
      
      if (!extractResponse.ok) {
        const errorData = await extractResponse.json();
        throw new Error(errorData.detail || 'Failed to extract audio');
      }
      
      const extractData = await extractResponse.json();
      progressUpdates = [...progressUpdates, ...extractData.progress_updates];
      
      if (!extractData.file_path) {
        throw new Error('No audio file path returned from extraction');
      }
      
      // Clone the voice using the extracted audio file
      progressUpdates = [...progressUpdates, "Creating voice clone..."];
      const cloneResponse = await fetch('http://localhost:8000/clone-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio_file: extractData.file_path })
      });
      
      if (!cloneResponse.ok) {
        const errorData = await cloneResponse.json();
        throw new Error(errorData.detail || 'Failed to clone voice');
      }
      
      const cloneData = await cloneResponse.json();
      progressUpdates = [...progressUpdates, "Voice clone created successfully!"];
      
      // Show the save dialog
      currentVoiceId = cloneData.voice_id;
      progressMessage = 'Voice clone created successfully!';
      
    } catch (e) {
      error = e.message;
      progressUpdates = [...progressUpdates, `Error: ${e.message}`];
    } finally {
      isProcessing = false;
    }
  }

  async function saveVoice() {
    if (!currentVoiceId || !voiceName) return;
    
    try {
      const response = await fetch(`http://localhost:8000/save-voice?voice_id=${currentVoiceId}`, {
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
      progressMessage = '';
    } catch (e) {
      error = e.message;
    }
  }

  async function loadVoices() {
    try {
      const response = await fetch('http://localhost:8000/voices').catch(() => {
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

      const response = await fetch('http://localhost:8000/speak', {
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
      const response = await fetch('http://localhost:8000/speak', {
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
      const response = await fetch(`http://localhost:8000/voices/${encodeURIComponent(name)}`, {
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
</script>

<main class="container">
  <h1>Voice Cloning App</h1>
  
  {#if error}
    <div class="error">
      {error}
    </div>
  {/if}

  {#if progressMessage}
    <div class="progress">
      {progressMessage}
    </div>
  {/if}

  <div class="youtube-section">
    <h2>Clone Voice from YouTube</h2>
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
    
    {#if progressUpdates.length > 0}
      <div class="progress-container">
        {#each progressUpdates as update}
          <div class="progress-update" class:error={update.startsWith('Error')} class:success={update.includes('success')}>
            {update}
          </div>
        {/each}
      </div>
    {/if}
    
    {#if error}
      <div class="error-message">{error}</div>
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
  }

  h1 {
    color: #2c3e50;
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

  .progress {
    background-color: #2ecc71;
    color: white;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    text-align: center;
  }

  .youtube-section {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 4px;
    margin-bottom: 2rem;
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

  .progress-container {
    margin: 20px 0;
    padding: 15px;
    border-radius: 8px;
    background: #f5f5f5;
    max-height: 200px;
    overflow-y: auto;
  }
  
  .progress-update {
    margin: 8px 0;
    padding: 8px;
    border-radius: 4px;
    background: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
  
  .progress-update.error {
    background: #fee;
    color: #c00;
  }
  
  .progress-update.success {
    background: #efe;
    color: #0a0;
  }
  
  .spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 10px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>
