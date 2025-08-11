class TypingTestApp {
    constructor() {
        this.testText = '';
        this.words = [];
        this.currentWordIndex = 0;
        this.startTime = 0;
        this.testDuration = 60;
        this.timer = null;
        this.isTestActive = false;
        this.corporaData = [];
        this.currentInput = '';
        this.typedWords = [];
        this.incorrectWords = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadCorporaData();
        this.loadSampleText();
    }
    
    initializeElements() {
        this.textDisplay = document.getElementById('text-display');
        this.textLine = document.getElementById('text-line');
        this.typingInput = document.getElementById('typing-input');
        this.resetBtn = document.getElementById('reset-btn');
        this.resultsPanel = document.getElementById('results-panel');
        this.liveStats = document.getElementById('live-stats');
        this.newTestBtn = document.getElementById('new-test-btn');
        
        this.testDurationSelect = document.querySelectorAll('.time-btn');
        
        this.wpmResult = document.getElementById('wpm-result');
        this.accuracyResult = document.getElementById('accuracy-result');
        this.timeResult = document.getElementById('time-result');
        this.wordsResult = document.getElementById('words-result');
        
        this.timeLeft = document.getElementById('time-left');
        this.currentWpm = document.getElementById('current-wpm');
        this.currentAccuracy = document.getElementById('current-accuracy');
    }
    
    bindEvents() {
        this.newTestBtn.addEventListener('click', () => this.newTest());
        this.resetBtn.addEventListener('click', () => this.resetTest());
        this.typingInput.addEventListener('input', (e) => this.handleTyping(e));
        this.typingInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        this.testDurationSelect.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.testDurationSelect.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.testDuration = parseInt(e.target.dataset.time);
                this.updateTimeDisplay();
            });
        });
    }
    
    async loadCorporaData() {
        try {
            const bbcRes = await this.findAvailableBBCResource();
            if (bbcRes) {
                const { path, text, contentType } = bbcRes;
                if (contentType && contentType.includes('application/json')) {
                    this.parseBBCNewsJSON(text);
                } else {
                    this.parseBBCNewsText(text);
                }
                console.log(`Loaded BBC News corpus from ${path}`);
                return;
            }
        } catch (err) {
            console.warn('BBC News corpus load failed:', err);
        }

        try {
            const response = await fetch('corpora/unigram_freq.csv');
            const csvText = await response.text();
            this.parseUnigramCSVData(csvText);
            console.log('Loaded unigram corpus as fallback');
            return;
        } catch (err) {
            console.warn('Unigram corpus load failed:', err);
        }

        this.loadFallbackData();
    }

    async findAvailableBBCResource() {
        const candidates = [
            'corpora/bbc-news.csv',
            'corpora/bbc_news.csv',
            'corpora/bbc-news.json',
            'corpora/bbc_news.json',
            'corpora/bbc-news.txt',
            'corpora/bbc_news.txt'
        ];
        for (const path of candidates) {
            try {
                const res = await fetch(path, { method: 'GET', cache: 'no-cache' });
                if (!res.ok) continue;
                const contentType = res.headers.get('content-type') || '';
                const text = await res.text();

                if (contentType.includes('text/html') || this.isProbablyHtml(text)) {
                    continue;
                }
                return { path, text, contentType };
            } catch (_) {

            }
        }
        return null;
    }

    isProbablyHtml(text) {
        if (!text) return false;
        const snippet = text.slice(0, 200).toLowerCase();
        return snippet.includes('<!doctype html') || snippet.includes('<html') || snippet.includes('<head') || snippet.includes('<div');
    }

    parseBBCNewsJSON(jsonText) {
        try {
            const data = JSON.parse(jsonText);

            const items = Array.isArray(data) ? data : (Array.isArray(data.items) ? data.items : []);
            const texts = [];
            for (const item of items) {
                const fields = [
                    item.text, item.content, item.article, item.body,
                    item.description, item.summary, item.title
                ].filter(Boolean);
                if (fields.length > 0) {
                    texts.push(fields.join('. '));
                }
            }
            if (texts.length === 0) {

                this.parseBBCNewsText(jsonText);
                return;
            }
            const combined = texts.join('\n');
            this.parseBBCNewsText(combined);
        } catch (e) {
            console.warn('Failed to parse BBC JSON, falling back to raw text:', e);
            this.parseBBCNewsText(jsonText);
        }
    }

    parseBBCNewsText(rawText) {

        const noTags = rawText
            .replace(/<[^>]*>/g, ' ') 
            .replace(/&[a-z]+;/gi, ' '); 

        const lines = noTags.split(/\r?\n/);
        let contentOnly = noTags;
        if (lines.length > 0 && /[,;]|\t/.test(lines[0])) {
            contentOnly = lines.slice(1).join(' ');
        }

        const sentenceMatches = contentOnly.match(/[^.!?\n]+[.!?]?/g) || [contentOnly];
        const sentencePhrases = [];
        const allWords = [];
        const bannedWords = new Set([
            'div','span','meta','button','label','line','stat','info','time','logo','mono','script','style','link','head','html','body','class','id','data','result','family'
        ]);

        for (const s of sentenceMatches) {
            const words = (s.toLowerCase().match(/[a-z]+/g) || []);
            const filtered = [];
            for (const w of words) {
                if (bannedWords.has(w)) continue;
                if (!this.isCommonWord(w)) continue;
                if (filtered.length > 0 && filtered[filtered.length - 1] === w) continue; 
                filtered.push(w);
            }

            const unique = [];
            const seen = new Set();
            for (const w of filtered) {
                if (seen.has(w)) continue;
                seen.add(w);
                unique.push(w);
            }
            if (unique.length >= 12 && unique.length <= 30) {
                sentencePhrases.push(unique.join(' '));
            }
            for (const w of unique) allWords.push(w);
            if (sentencePhrases.length >= 80) break; 
        }

        if (sentencePhrases.length < 10 && allWords.length > 0) {
            this.allWords = Array.from(new Set(allWords));
            this.shuffleArray(this.allWords);
            const extra = [];
            for (let i = 0; i < 30; i++) {
                extra.push(this.generateNewTextFromWords());
            }
            sentencePhrases.push(...extra);
        }

        this.allWords = allWords.length ? Array.from(new Set(allWords)) : (contentOnly.toLowerCase().match(/[a-z]+/g) || []);
        this.corporaData = sentencePhrases.length ? sentencePhrases : [this.generateNewTextFromWords()];

        console.log(`BBC News parsing complete. Sentences: ${this.corporaData.length}, Word pool: ${this.allWords.length}`);
    }
    
    parseUnigramCSVData(csvText) {
        const lines = csvText.split('\n');
        const allWords = [];
        let totalWords = 0;
        let filteredWords = 0;
        
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line) {
                const parts = line.split(',');
                if (parts.length >= 1) {
                    const word = parts[0].trim(); 
                    if (word && word.length > 0) {
                        totalWords++;

                        if (this.isCommonWord(word)) {
                            allWords.push(word);
                            filteredWords++;
                        }
                    }
                }
            }
        }
        
        console.log(`Total words in corpus: ${totalWords}`);
        console.log(`Words after filtering: ${filteredWords}`);
        console.log(`Filtering ratio: ${Math.round((filteredWords/totalWords)*100)}%`);
        
        this.allWords = allWords;
        
        this.shuffleArray(allWords);
        
        const texts = [];
        const phraseLengths = [15, 18, 20, 22, 25, 28, 30]; 
        
        for (let i = 0; i < 20; i++) { 
            const phraseLength = phraseLengths[Math.floor(Math.random() * phraseLengths.length)];
            const startIndex = (i * phraseLength) % allWords.length;
            
            let phrase = '';
            for (let j = 0; j < phraseLength; j++) {
                const wordIndex = (startIndex + j) % allWords.length;
                phrase += allWords[wordIndex] + ' ';
            }
            
            texts.push(phrase.trim());
        }
        
        this.shuffleArray(texts);
        
        this.corporaData = texts;
        console.log(`Created ${texts.length} shuffled texts from ${allWords.length} common words`);
        
        if (allWords.length > 0) {
            console.log('Sample words from corpus:', allWords.slice(0, 20).join(', '));
        }
    }
    
    isCommonWord(word) {
        const wordLower = word.toLowerCase();
        
        if (wordLower.length < 2) return false;
        
        if (wordLower.length > 8) return false;
        
        if (!/^[a-zA-Z]+$/.test(wordLower)) return false;
        
        const familiarWords = [
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'may', 'any', 'few', 'own', 'why', 'yes', 'no', 'go', 'up', 'in', 'on', 'at', 'by', 'to', 'of', 'as', 'so', 'if', 'or', 'an', 'my', 'me', 'he', 'we', 'do', 'be', 'it', 'is', 'am', 'us', 'my', 'me', 'he', 'we', 'do', 'be', 'it', 'is', 'am', 'us',
            
            'about', 'after', 'again', 'could', 'every', 'first', 'found', 'great', 'house', 'large', 'might', 'never', 'other', 'place', 'right', 'small', 'sound', 'still', 'their', 'there', 'think', 'three', 'under', 'water', 'where', 'which', 'while', 'world', 'would', 'write', 'people', 'through', 'during', 'before', 'should', 'being', 'having', 'doing', 'going', 'coming', 'seeing', 'knowing', 'working', 'looking', 'talking', 'walking', 'running', 'sitting', 'standing', 'waiting', 'helping', 'making', 'taking', 'giving', 'sending', 'bringing', 'finding', 'keeping', 'leaving', 'starting', 'stopping', 'opening', 'closing', 'moving', 'changing', 'growing', 'showing', 'telling', 'asking', 'reading', 'writing', 'speaking', 'listening', 'watching', 'playing', 'eating', 'drinking', 'sleeping', 'waking', 'living', 'loving', 'wanting', 'needing', 'hoping', 'believing', 'knowing', 'learning', 'teaching', 'buying', 'selling', 'building', 'creating', 'beginning', 'ending', 'winning', 'losing', 'catching', 'throwing', 'hitting', 'missing', 'breaking', 'fixing', 'pushing', 'pulling', 'lifting', 'dropping', 'carrying', 'holding', 'touching', 'feeling', 'smelling', 'tasting', 'hearing',
            
            'another', 'because', 'between', 'different', 'important', 'something', 'sometimes', 'together', 'without', 'anything', 'everything', 'everybody', 'somebody', 'nobody', 'anybody', 'everyone', 'someone', 'anyone', 'nothing', 'anywhere', 'everywhere', 'somewhere', 'nowhere', 'anytime', 'sometime', 'everyday', 'somehow', 'anyway', 'anyhow', 'somewhat', 'anywhere', 'everywhere', 'somewhere', 'nowhere', 'anytime', 'sometime', 'everyday', 'somehow', 'anyway', 'anyhow', 'somewhat'
        ];
        
        if (familiarWords.includes(wordLower)) return true;

        if (wordLower.length > 6) return false; 
        
        const vowels = wordLower.match(/[aeiou]/g);
        const consonants = wordLower.match(/[bcdfghjklmnpqrstvwxyz]/g);
        
        if (vowels && consonants) {
            const vowelRatio = vowels.length / wordLower.length;
            if (vowelRatio < 0.25 || vowelRatio > 0.75) return false;
        }
        
        const consonantClusters = /[bcdfghjklmnpqrstvwxyz]{3,}/;
        if (consonantClusters.test(wordLower)) return false;
        
        const unusualCombos = /[q][^u]|[x][^aeiou]|[z][^aeiou]/;
        if (unusualCombos.test(wordLower)) return false;
        
        return true;
    }
    
    loadFallbackData() {
        this.corporaData = [
            "The quick brown fox jumps over the lazy dog. This is a simple test.",
            "A man walked down the street and saw a cat. The cat was black and white.",
            "In the morning I like to drink coffee and read books. It helps me wake up.",
            "She went to the store to buy some food. The store was very busy today.",
            "We can go to the park or stay at home. Both options sound good to me.",
            "The weather is nice today so we should go outside. Fresh air is good for you.",
            "My friend called me yesterday and we talked for hours. It was really fun.",
            "I need to finish my work before dinner time. There is still much to do.",
            "The children played in the garden while their parents watched from the house.",
            "Please remember to bring your keys when you leave the house today."
        ];
        console.log('Using fallback corpus data with common words');
    }
    
    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
    
    loadSampleText() {
        if (this.allWords && this.allWords.length > 0) {
            this.testText = this.generateNewTextFromWords();
        } else if (this.corporaData.length > 0) {
            this.testText = this.corporaData[Math.floor(Math.random() * this.corporaData.length)];
        } else {
            this.testText = "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet at least once.";
        }
        
        this.words = this.testText.split(/\s+/);
        this.displayText();
    }
    
    displayText() {
        this.textLine.innerHTML = '';
        this.words.forEach((word, index) => {
            const wordSpan = document.createElement('span');
            wordSpan.textContent = word;
            wordSpan.className = 'word';
            wordSpan.dataset.index = index;
            this.textLine.appendChild(wordSpan);
            if (index < this.words.length - 1) {
                this.textLine.appendChild(document.createTextNode(' '));
            }
        });
        this.highlightCurrentWord();
    }
    
    highlightCurrentWord() {
        this.textLine.querySelectorAll('.word').forEach(word => {
            word.classList.remove('current', 'correct', 'incorrect');
        });
        
        if (this.currentWordIndex < this.words.length) {
            const currentWord = this.textLine.querySelector(`[data-index="${this.currentWordIndex}"]`);
            if (currentWord) {
                currentWord.classList.add('current');
            }
        }
        
        for (let i = 0; i < this.currentWordIndex; i++) {
            const word = this.textLine.querySelector(`[data-index="${i}"]`);
            if (word) {
                if (this.typedWords[i] === this.words[i]) {
                    word.classList.add('correct');
                } else {
                    word.classList.add('incorrect');
                }
            }
        }
    }
    
    startTest() {
        if (this.isTestActive) return;
        
        this.isTestActive = true;
        this.startTime = Date.now();
        this.currentWordIndex = 0;
        this.typedWords = [];
        this.incorrectWords = [];
        this.currentInput = '';
        
        this.typingInput.disabled = false;
        this.typingInput.value = '';
        this.typingInput.focus();
        
        this.liveStats.style.display = 'grid';
        this.liveStats.classList.add('fade-in');
        
        this.resultsPanel.style.display = 'none';
        
        this.startTimer();
        
        this.loadNewText();
    }
    
    loadNewText() {
        if (Math.random() < 0.7 && this.corporaData.length > 1) {
            const availableTexts = this.corporaData.filter(text => 
                text !== this.testText
            );
            
            if (availableTexts.length > 0) {
                this.testText = availableTexts[Math.floor(Math.random() * availableTexts.length)];
            } else {
                this.shuffleArray(this.corporaData);
                this.testText = this.corporaData[0];
            }
        } else {
            this.testText = this.generateNewTextFromWords();
        }
        
        this.words = this.testText.split(/\s+/);
        this.displayText();
    }
    
    startTimer() {
        const updateTimer = () => {
            if (!this.isTestActive) return;
            
            const elapsed = (Date.now() - this.startTime) / 1000;
            const remaining = this.testDuration - elapsed;
            
            if (remaining <= 0) {
                this.endTest();
                return;
            }
            
            this.updateTimeDisplay(remaining);
            
            const currentWpm = this.calculateCurrentWpm(elapsed);
            this.currentWpm.textContent = currentWpm;
            
            const currentAccuracy = this.calculateCurrentAccuracy();
            this.currentAccuracy.textContent = `${currentAccuracy}%`;
            
            this.timer = setTimeout(updateTimer, 100);
        };
        
        updateTimer();
    }
    
    updateTimeDisplay(remaining = this.testDuration) {
        const minutes = Math.floor(remaining / 60);
        const seconds = Math.floor(remaining % 60);
        this.timeLeft.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    calculateCurrentWpm(elapsed) {
        const typedWords = this.typedWords.filter(word => word !== '').length;
        const minutes = elapsed / 60;
        return minutes > 0 ? Math.round(typedWords / minutes) : 0;
    }
    
    calculateCurrentAccuracy() {
        if (this.currentWordIndex === 0) return 100;
        let correctWords = 0;
        for (let i = 0; i < this.currentWordIndex; i++) {
            if (this.typedWords[i] === this.words[i]) {
                correctWords++;
            }
        }
        return Math.round((correctWords / this.currentWordIndex) * 100);
    }
    
    handleTyping(e) {
        if (!this.isTestActive) return;
        
        const input = e.target.value;
        const currentWord = this.words[this.currentWordIndex];
        
        if (currentWord && input.endsWith(' ')) {
            const typedWord = input.trim();
            this.typedWords[this.currentWordIndex] = typedWord;
            
            if (typedWord !== currentWord) {
                this.incorrectWords.push({
                    expected: currentWord,
                    typed: typedWord,
                    position: this.currentWordIndex
                });
            }
            
            this.currentWordIndex++;
            this.currentInput = '';
            e.target.value = '';
            
            if (this.currentWordIndex >= this.words.length) {
                this.generateMoreText();
            }
            
            this.highlightCurrentWord();
        } else {
            this.currentInput = input;
        }
    }
    
    handleKeydown(e) {
        if (!this.isTestActive) return;
        
        if (e.key === 'Enter' && e.shiftKey && e.ctrlKey) {
            e.preventDefault();
            this.newTest();
        }
        
        if (e.key === 'Escape') {
            e.preventDefault();
        }
    }
    
    generateMoreText() {
        this.loadNewText();
        this.currentWordIndex = 0;
        this.typedWords = [];
        this.incorrectWords = [];
        this.displayText();
    }
    
    endTest() {
        this.isTestActive = false;
        clearTimeout(this.timer);
        
        const endTime = Date.now();
        const timeTaken = (endTime - this.startTime) / 1000;
        
        const results = this.calculateResults(timeTaken);
        
        this.displayResults(results);
        
        this.typingInput.disabled = true;
        this.liveStats.style.display = 'none';
    }
    
    calculateResults(timeTaken) {
        const wordCount = this.typedWords.filter(word => word !== '').length;
        const wpm = timeTaken > 0 ? Math.round((wordCount / timeTaken) * 60) : 0;
        
        const totalWords = this.currentWordIndex;
        const correctWords = totalWords - this.incorrectWords.length;
        const accuracy = totalWords > 0 ? Math.round((correctWords / totalWords) * 100) : 0;
        
        return {
            wpm: wpm,
            accuracy: accuracy,
            timeTaken: Math.round(timeTaken * 100) / 100,
            wordCount: wordCount,
            charCount: this.typedWords.join(' ').length,
            incorrectWords: this.incorrectWords
        };
    }
    
    displayResults(results) {
        this.wpmResult.textContent = results.wpm;
        this.accuracyResult.textContent = `${results.accuracy}%`;
        this.timeResult.textContent = `${results.timeTaken}s`;
        this.wordsResult.textContent = results.wordCount;
        
        this.resultsPanel.style.display = 'block';
        this.resultsPanel.classList.add('slide-up');
    }
    
    resetTest() {
        this.isTestActive = false;
        clearTimeout(this.timer);
        
        this.currentWordIndex = 0;
        this.typedWords = [];
        this.incorrectWords = [];
        this.currentInput = '';
        
        this.typingInput.disabled = false;
        this.typingInput.value = '';
        this.liveStats.style.display = 'none';
        this.resultsPanel.style.display = 'none';
        
        this.loadSampleText();
    }
    
    newTest() {
        this.resetTest();
        this.startTest();
    }

    generateNewTextFromWords() {
        const phraseLengths = [15, 18, 20, 22, 25, 28, 30];
        const phraseLength = phraseLengths[Math.floor(Math.random() * phraseLengths.length)];
        
        let newText = '';
        let lastWord = '';
        let lastWordType = '';
        const banned = new Set(['div','span','meta','button','label','line','stat','info','time','logo','mono','script','style','link','head','html','body','class','id','data','result','family']);
        const used = new Set();
        
        for (let i = 0; i < phraseLength; i++) {
            let selectedWord;
            let attempts = 0;
            do {
                if (i === 0) {
                    const starters = ['the','a','in','on','at','by','for','with','to','of','and','but','or','so','if','when','while','because','although','this','that','these','those','some','many','few','each','every','any','all','both','either','neither'];
                    const starterWords = this.allWords.filter(word => starters.includes(word.toLowerCase()));
                    selectedWord = starterWords.length ? starterWords[Math.floor(Math.random() * starterWords.length)] : this.allWords[Math.floor(Math.random() * this.allWords.length)];
                    lastWordType = 'starter';
                } else {
                    selectedWord = this.allWords[Math.floor(Math.random() * this.allWords.length)];
                    lastWordType = 'content';
                }
                attempts++;
                if (attempts > 20) break;
            } while (
                !selectedWord ||
                banned.has(selectedWord.toLowerCase()) ||
                selectedWord === lastWord ||
                used.has(selectedWord)
            );

            newText += selectedWord + ' ';
            used.add(selectedWord);
            lastWord = selectedWord;
        }
        
        return newText.trim();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const app = new TypingTestApp();
    
    document.getElementById('typing-input').disabled = false;
    
    document.getElementById('typing-input').addEventListener('focus', () => {
        if (!app.isTestActive) {
            app.startTest();
        }
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.shiftKey && e.ctrlKey) {
            e.preventDefault();
            app.newTest();
        }
    });
});

export default TypingTestApp; 