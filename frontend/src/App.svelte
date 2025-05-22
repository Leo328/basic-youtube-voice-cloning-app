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

  async function extractAudio(url: string) {
    const response = await fetch('http://localhost:8000/extract-audio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to extract audio');
    }

    return response.json();
  }

  async function handleSubmit() {
    loading = true;
    extractingAudio = true;
    error = null;
    progressMessage = 'Opening browser to extract audio...';
    
    try {
      // First extract the audio
      const audioResult = await extractAudio(youtubeUrl);
      if (audioResult.status !== 'success') {
        throw new Error(audioResult.message || 'Failed to extract audio');
      }

      progressMessage = 'Audio extracted, creating voice clone...';
      
      // Clone voice from YouTube
      const response = await fetch('http://localhost:8000/clone-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: youtubeUrl })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to clone voice');
      }
      
      const { voice_id } = await response.json();
      currentVoiceId = voice_id;
      progressMessage = 'Voice clone created successfully!';
      
    } catch (e) {
      error = e.message;
      progressMessage = '';
    } finally {
      loading = false;
      extractingAudio = false;
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
      const response = await fetch('http://localhost:8000/voices');
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load voices');
      }
      voices = await response.json();
    } catch (e) {
      error = e.message;
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

  <form on:submit|preventDefault={handleSubmit} class="youtube-form">
    <input
      type="text"
      bind:value={youtubeUrl}
      placeholder="Enter YouTube URL"
      disabled={loading}
    />
    <button type="submit" disabled={loading || !youtubeUrl}>
      {loading ? 'Processing...' : 'Clone Voice'}
    </button>
  </form>

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
            <button on:click={() => playQuestion(id)}>
              Play Sample
            </button>
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

  .youtube-form {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
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

  .input-group {
    display: flex;
    gap: 1rem;
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
</style>
