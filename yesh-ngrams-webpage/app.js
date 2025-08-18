// typing_test.js (web) — mirrors naming from N-grams folder
document.addEventListener('DOMContentLoaded', () => {
	const search = new URLSearchParams(location.search);
	const difficulty = (search.get('difficulty') || 'medium').toLowerCase();

	const hiddenInput = document.getElementById('hiddenInput');
	const textArea = document.getElementById('textArea');
	const newTestBtn = document.getElementById('newTestBtn');
	const restartBtn = document.getElementById('restartBtn');
	const timeOptions = document.querySelectorAll('.time-option');

	let testActive = false;
	let startTime = null;
	let testDuration = 60;
	let allWords = [];
	let currentWordIndex = 0; // global index across full text
	let pageStartIndex = 0;
	let pageWordCount = 0;
	let typedWords = [];
	let incorrectWords = [];
	let grossCharsTyped = 0; // for WPM (typed chars)
	let accCorrectChars = 0; // for accuracy numerator
	let accTotalChars = 0;   // for accuracy denominator (correct+incorrect+extra+missed)
	let totalWordsTyped = 0;
	let correctWordsTyped = 0;

	function pickText() {
		const corp = (window.CORPORA && window.CORPORA[difficulty]) || [];
		const pool = corp.length ? corp : (window.CORPORA ? (window.CORPORA.medium || []) : []);
		const phrases = generatePhrasesFromCorpus(pool, difficulty, testDuration);
		const text = phrases.join(' ');
		allWords = text.split(/\s+/);
		renderPage(true);
	}

	function startTest() {
		if (testActive) return;
		testActive = true;
		startTime = Date.now();
		currentWordIndex = 0;
		typedWords = [];
		incorrectWords = [];
		grossCharsTyped = 0;
		accCorrectChars = 0;
		accTotalChars = 0;
		totalWordsTyped = 0;
		correctWordsTyped = 0;
		pickText();
		hiddenInput.focus();
		updateTimer();
		const timerInterval = setInterval(updateTimer, 1000);
		const endInterval = setInterval(() => {
			if (Date.now() - startTime >= testDuration * 1000) {
				clearInterval(timerInterval);
				clearInterval(endInterval);
				endTest();
			}
		}, 1000);
	}

	function endTest() {
		testActive = false;
		const elapsed = (Date.now() - startTime) / 1000;
		const minutes = Math.max(1e-6, elapsed / 60);
		const wpm = Math.round((grossCharsTyped / 5) / minutes);
		const accuracy = accTotalChars > 0 ? Math.round((accCorrectChars / accTotalChars) * 100) : 100;
		document.getElementById('resultWpm').textContent = wpm;
		document.getElementById('resultAccuracy').textContent = accuracy + '%';
		document.getElementById('resultTime').textContent = formatTime(elapsed);
		document.getElementById('resultWords').textContent = totalWordsTyped;
		document.getElementById('testCompleteModal').style.display = 'flex';
		document.getElementById('cursorIndicator').style.display = 'none';
	}

	function processWord(word) {
		if (!testActive) return;
		typedWords.push(word);
		const expected = allWords[currentWordIndex];
		const isCorrect = word === expected;
		const el = document.querySelector(`[data-gidx="${currentWordIndex}"]`);
		if (el) {
			el.classList.remove('current');
			el.classList.add(isCorrect ? 'correct' : 'incorrect');
		}
		if (!isCorrect) incorrectWords.push({ expected, typed: word, position: currentWordIndex });
		// Stats
		totalWordsTyped += 1;
		grossCharsTyped += word.length; // only what the user typed counts for WPM
		// Character accounting for accuracy (Monkeytype-like)
		const stats = compareWordChars(word, expected);
		accCorrectChars += stats.matches;
		accTotalChars += stats.matches + stats.incorrect + stats.extra + stats.missed;
		if (normalizeWord(word) === normalizeWord(expected)) correctWordsTyped += 1;
		currentWordIndex++;
		updateDisplay();
		if (currentWordIndex >= pageStartIndex + pageWordCount) {
			advancePage();
		}
	}

	function renderPage(animated = false) {
		const textArea = document.getElementById('textArea');
		const textContent = document.getElementById('textContent');
		pageWordCount = computeFittingCount(textArea, textContent, pageStartIndex);
		textContent.innerHTML = '';
		for (let i = 0; i < pageWordCount; i++) {
			const gidx = pageStartIndex + i;
			const w = allWords[gidx] || '';
			const span = document.createElement('span');
			span.textContent = w + ' ';
			span.className = 'word';
			span.dataset.gidx = String(gidx);
			textContent.appendChild(span);
		}
		if (animated) {
			textContent.classList.remove('slide-up');
			// force reflow
			void textContent.offsetWidth;
			textContent.classList.add('slide-up');
		}
		updateDisplay();
	}

	function computeFittingCount(containerEl, contentEl, startIndex) {
		const maxIndex = allWords.length;
		let count = 0;
		contentEl.innerHTML = '';
		const buffer = document.createDocumentFragment();
		while (startIndex + count < maxIndex) {
			const gidx = startIndex + count;
			const span = document.createElement('span');
			span.textContent = (allWords[gidx] || '') + ' ';
			span.className = 'word';
			span.dataset.gidx = String(gidx);
			buffer.appendChild(span);
			contentEl.appendChild(span);
			// Allow content to layout, then check overflow
			if (contentEl.scrollHeight > containerEl.clientHeight - 6) {
				// remove last overflowed span and stop
				contentEl.removeChild(span);
				break;
			}
			count++;
		}
		return Math.max(1, count);
	}

	function advancePage() {
		// move start to currentWordIndex to keep cursor at top row
		pageStartIndex = currentWordIndex;
		renderPage(true);
	}

	function updateDisplay() {
		const els = document.querySelectorAll('.word');
		els.forEach((el, i) => {
			const wasCorrect = el.classList.contains('correct');
			const wasIncorrect = el.classList.contains('incorrect');
			const gidx = parseInt(el.dataset.gidx || '-1', 10);
			el.className = 'word';
			if (gidx < currentWordIndex) {
				if (wasCorrect) el.classList.add('correct');
				else if (wasIncorrect) el.classList.add('incorrect');
			} else if (gidx === currentWordIndex) {
				el.classList.add('current');
			}
		});
	}

	function updateCurrentWordDisplay(typedText, expectedWord) {
		if (!expectedWord) return;
		const el = document.querySelector(`[data-gidx="${currentWordIndex}"]`);
		if (!el) return;
		let html = '';
		for (let i = 0; i < Math.max(typedText.length, expectedWord.length); i++) {
			if (i < typedText.length && i < expectedWord.length) {
				html += typedText[i] === expectedWord[i]
					? `<span class="char correct-char">${typedText[i]}</span>`
					: `<span class="char incorrect-char">${typedText[i]}</span>`;
			} else if (i < typedText.length) {
				html += `<span class="char extra-char">${typedText[i]}</span>`;
			} else if (i < expectedWord.length) {
				html += `<span class="char expected-char">${expectedWord[i]}</span>`;
			}
		}
		el.innerHTML = html;
	}

	function normalizeWord(s) { return (s || '').toLowerCase().replace(/[^a-z0-9]+/gi, ''); }
	function compareWordChars(typed, expected) {
		const a = (typed || '').toLowerCase();
		const b = (expected || '').toLowerCase();
		let matches = 0;
		let incorrect = 0;
		const L = Math.min(a.length, b.length);
		for (let i = 0; i < L; i++) {
			if (a[i] === b[i]) matches++; else incorrect++;
		}
		const extra = Math.max(0, a.length - b.length);
		const missed = Math.max(0, b.length - a.length);
		return { matches, incorrect, extra, missed };
	}

	function updateCursorPosition() {
		const cursor = document.getElementById('cursorIndicator');
		const el = document.querySelector(`[data-index="${currentWordIndex}"]`);
		if (!el) return;
		const rect = el.getBoundingClientRect();
		const area = document.getElementById('textArea').getBoundingClientRect();
		const inputLength = hiddenInput.value.length;
		const charWidth = rect.width / Math.max(1, el.textContent.length);
		const x = rect.left - area.left + (inputLength * charWidth);
		const y = rect.top - area.top;
		cursor.style.left = x + 'px';
		cursor.style.top = y + 'px';
		cursor.style.display = 'block';
	}

	function updateTimer() {
		if (!testActive || !startTime) return;
		const elapsed = (Date.now() - startTime) / 1000;
		const remaining = Math.max(0, testDuration - elapsed);
		document.getElementById('timeRemaining').textContent = formatTime(remaining);
	}

	function formatTime(seconds) {
		const m = Math.floor(seconds / 60);
		const s = Math.floor(seconds % 60);
		return `${m}:${s.toString().padStart(2, '0')}`;
	}

	function setTestDuration(d) { testDuration = d; }
	function updateTimeOptions() {
		timeOptions.forEach(opt => {
			opt.classList.toggle('active', parseInt(opt.dataset.duration) === testDuration);
		});
	}

	// ---- N-grams inspired phrase generation (wordlist sampling) ----
	function generatePhrasesFromCorpus(lines, mode, timeLimitSeconds) {
		const tokens = tokenizeLines(lines);
		if (tokens.length === 0) return ['keep typing to begin the test'];
		const alphaTokens = tokens.filter(t => /^[a-z]+$/.test(t));
		const freq = countFrequencies(alphaTokens);
		let vocabulary = uniquePreserve(alphaTokens);
		// Difficulty word-length ranges
		function inLengthRange(w) {
			const L = w.length;
			if (mode === 'easy') return L <= 4;
			if (mode === 'medium') return L >= 5 && L <= 7;
			return L >= 8; // hard
		}
		vocabulary = vocabulary.filter(inLengthRange);
		// Additional quality filters per mode
		if (mode === 'easy') {
			const commonTwo = new Set(['of','to','in','is','on','by','or','at','an','as','it','be','he','we','me','my','do','go','no','so','up','us']);
			const filtered = [];
			for (const w of vocabulary) {
				const L = w.length;
				if (L === 2) {
					if (commonTwo.has(w)) filtered.push(w);
					continue;
				}
				if (L >= 3) {
					if (containsVowel(w) && (freq[w] || 0) >= 2) filtered.push(w);
				}
			}
			if (filtered.length >= Math.max(10, getTargetPhraseLength(mode))) vocabulary = filtered;
		} else if (mode === 'medium') {
			const med = vocabulary.filter(w => (freq[w] || 0) >= 2);
			if (med.length >= Math.max(20, getTargetPhraseLength(mode))) vocabulary = med;
		} else {
			const hard = vocabulary.filter(w => (freq[w] || 0) >= 1);
			if (hard.length >= Math.max(20, getTargetPhraseLength(mode))) vocabulary = hard;
		}

		// Estimate phrase count to fit time limit (chars/sec baseline ~8)
		const { baseTargetLen, avgWordLen } = difficultyParams(mode);
		const approxCharsPerPhrase = Math.max(1, Math.round(baseTargetLen * (avgWordLen + 1)));
		const minChars = Math.max(80, Math.round(timeLimitSeconds * 8));
		let numPhrases = Math.max(5, Math.min(40, Math.ceil(minChars / approxCharsPerPhrase)));

		const phrases = generateUniqueWordlistPhrases(vocabulary, numPhrases, mode);
		// Top up once if still short
		const combined = phrases.join(' ');
		if (combined.length < minChars) {
			const extraNeeded = minChars - combined.length;
			const extraCount = Math.max(3, Math.ceil(extraNeeded / approxCharsPerPhrase));
			phrases.push(...generateUniqueWordlistPhrases(vocabulary, extraCount, mode));
		}
		return phrases;
	}

	function tokenizeLines(lines) {
		const text = (lines || []).map(s => String(s).toLowerCase()).join('\n');
		// Split to sentences then words+punc; keep words only for phrase generation
		const rough = text.split(/\s+/g);
		return rough.map(t => t.replace(/[^a-z]/gi, '')).filter(Boolean);
	}

	function countFrequencies(arr) {
		const m = Object.create(null);
		for (const x of arr) m[x] = (m[x] || 0) + 1;
		return m;
	}

	function uniquePreserve(arr) {
		const seen = new Set();
		const out = [];
		for (const x of arr) if (!seen.has(x)) { seen.add(x); out.push(x); }
		return out;
	}

	function containsVowel(w) {
		return /[aeiou]/.test(w);
	}

	function getTargetPhraseLength(mode) {
		const base = { easy: 6, medium: 8, hard: 10 }[mode] || 8;
		return base + Math.floor(Math.random() * 4); // +0..3
	}

	function difficultyParams(mode) {
		if (mode === 'easy') return { baseTargetLen: 6, avgWordLen: 3.5 };
		if (mode === 'medium') return { baseTargetLen: 8, avgWordLen: 6.0 };
		return { baseTargetLen: 10, avgWordLen: 8.0 };
	}

	function generateUniqueWordlistPhrases(words, numPhrases, mode) {
		const phrases = [];
		const used = new Set();
		for (let k = 0; k < numPhrases; k++) {
			const targetLen = getTargetPhraseLength(mode);
			let available = words.filter(w => !used.has(w));
			let sampled = [];
			if (available.length >= targetLen) {
				sampled = sampleUnique(available, targetLen);
			} else if (available.length > 0) {
				sampled = available.slice();
				let remaining = targetLen - sampled.length;
				while (remaining > 0 && words.length > 0) {
					const cand = words[Math.floor(Math.random() * words.length)];
					if (sampled.length && cand === sampled[sampled.length - 1]) continue;
					sampled.push(cand);
					remaining--;
				}
			} else {
				for (let i = 0; i < targetLen; i++) {
					const cand = words[Math.floor(Math.random() * words.length)];
					if (sampled.length && cand === sampled[sampled.length - 1]) continue;
					sampled.push(cand);
				}
			}
			for (const w of sampled) used.add(w);
			phrases.push(sampled.join(' '));
		}
		return phrases;
	}

	function sampleUnique(arr, k) {
		const copy = arr.slice();
		const out = [];
		for (let i = 0; i < k && copy.length > 0; i++) {
			const idx = Math.floor(Math.random() * copy.length);
			out.push(copy[idx]);
			copy.splice(idx, 1);
		}
		return out;
	}

	// Events
	textArea.addEventListener('click', () => { if (!testActive) startTest(); hiddenInput.focus(); });
	hiddenInput.addEventListener('focus', () => { if (testActive) updateCursorPosition(); });
	hiddenInput.addEventListener('blur', () => { document.getElementById('cursorIndicator').style.display = 'none'; });
	hiddenInput.addEventListener('input', (e) => {
		if (!testActive) return;
		const input = e.target.value;
		const currentWord = allWords[currentWordIndex];
		if (input && input.includes(' ')) {
			const parts = input.split(' ');
			parts.forEach(w => { if (w.trim()) processWord(w.trim()); });
			e.target.value = '';
			updateCursorPosition();
		} else if (input) {
			updateCurrentWordDisplay(input, currentWord);
			updateCursorPosition();
		}
	});
	hiddenInput.addEventListener('keydown', (e) => {
		if (e.key === 'Tab' && e.shiftKey) { e.preventDefault(); restartTest(); }
		else if (e.key === 'Enter' && e.ctrlKey && e.shiftKey) { e.preventDefault(); newTest(); }
	});
	newTestBtn.addEventListener('click', newTest);
	restartBtn.addEventListener('click', restartTest);
	document.getElementById('backBtn').addEventListener('click', () => { window.location.href = 'index.html'; });
	timeOptions.forEach(opt => opt.addEventListener('click', function(){ setTestDuration(parseInt(this.dataset.duration)); updateTimeOptions(); if (testActive) newTest(); }));

	function newTest() {
		document.getElementById('testCompleteModal').style.display = 'none';
		document.getElementById('cursorIndicator').style.display = 'none';
		testActive = false; startTime = null; currentWordIndex = 0; typedWords = []; incorrectWords = []; grossCharsTyped = 0; accCorrectChars = 0; accTotalChars = 0; totalWordsTyped = 0; correctWordsTyped = 0;
		document.getElementById('timeRemaining').textContent = formatTime(testDuration);
		startTest();
	}

	function restartTest() {
		document.getElementById('testCompleteModal').style.display = 'none';
		document.getElementById('cursorIndicator').style.display = 'none';
		testActive = false; startTime = null; currentWordIndex = 0; typedWords = []; incorrectWords = []; grossCharsTyped = 0; accCorrectChars = 0; accTotalChars = 0; totalWordsTyped = 0; correctWordsTyped = 0;
		document.getElementById('timeRemaining').textContent = formatTime(testDuration);
		hiddenInput.value = '';
		pickText();
	}

	// Initialize
	updateTimeOptions();
	pickText();
});



