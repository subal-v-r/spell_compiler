document.addEventListener("DOMContentLoaded", () => {
    
    const compilerForm = document.getElementById("compilerForm");
    const fileInput = document.getElementById("fileInput");
    const fileName = document.getElementById("fileName");
    
    // Tabs setup
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));
            
            // Add active class to clicked
            btn.classList.add("active");
            document.getElementById(btn.dataset.target).classList.add("active");
        });
    });

    // File selection updating
    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            fileName.textContent = e.target.files[0].name;
            // Optionally clear text area when file selected
            document.getElementById("textInput").value = "";
        } else {
            fileName.textContent = "Select a .txt file";
        }
    });

    compilerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const textInput = document.getElementById("textInput").value.trim();
        const file = fileInput.files[0];
        
        if (!textInput && !file) {
            alert("Please enter text or upload a file.");
            return;
        }

        const btnText = document.querySelector("#compileBtn span");
        btnText.textContent = "Compiling...";
        document.getElementById("compileBtn").disabled = true;

        const formData = new FormData();
        if (file) {
            formData.append("file", file);
        } else {
            formData.append("text", textInput);
        }

        try {
            const response = await fetch("http://127.0.0.1:8000/compile", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Error compiling text.");
            }

            const data = await response.json();
            renderResults(data);
            document.getElementById("resultsSection").style.display = "block";
            
        } catch (error) {
            alert(error.message);
        } finally {
            btnText.textContent = "Compile";
            document.getElementById("compileBtn").disabled = false;
        }
    });
});

function renderResults(data) {
    // 1. Render Final Corrected View
    const finalView = document.getElementById("finalCorrectedText");
    finalView.textContent = data.corrected_text || "(Empty Output)";

    // 2. Render Spelling Issues
    const spellingList = document.getElementById("spellingErrorsList");
    spellingList.innerHTML = "";
    
    if (data.spelling_errors.length === 0) {
        spellingList.innerHTML = `<p style="color:var(--success)">✅ No spelling errors found during semantic phase.</p>`;
    } else {
        data.spelling_errors.forEach(err => {
            const card = document.createElement("div");
            card.className = "issue-card";
            
            const position = `[Ln ${err.line}, Col ${err.column}]`;
            
            let suggsHtml = err.suggestions.length > 0 
                ? err.suggestions.map(s => `<span class="suggestion-badge">${s}</span>`).join("")
                : `<span style="color:var(--text-muted); font-size:0.8rem">No suggestions found</span>`;

            card.innerHTML = `
                <div>${position} Invalid Token: <span class="issue-word">${err.word}</span></div>
                <div class="issue-suggestions">${suggsHtml}</div>
            `;
            spellingList.appendChild(card);
        });
    }

    // 3. Render Grammar Issues
    const grammarList = document.getElementById("grammarErrorsList");
    grammarList.innerHTML = "";
    
    if (data.grammar_issues.length === 0) {
        grammarList.innerHTML = `<p style="color:var(--success)">✅ No grammar violations detected.</p>`;
    } else {
        data.grammar_issues.forEach(err => {
            const card = document.createElement("div");
            card.className = "issue-card grammar";
            const position = `[Ln ${err.line}, Col ${err.column}]`;
            card.innerHTML = `
                <div>${position} <span class="issue-word grammar">${err.type}</span></div>
                <div style="font-size:0.9rem; margin-top:0.3rem">${err.message}</div>
            `;
            grammarList.appendChild(card);
        });
    }

    // 4. Render Tokens
    const tokensContainer = document.getElementById("tokensContainer");
    tokensContainer.innerHTML = "";
    
    data.tokens.forEach(tok => {
        const el = document.createElement("span");
        el.className = `token ${tok.type}`;
        
        let tVal = tok.value;
        if (tok.type === "WHITESPACE") {
            tVal = tok.value.replace(/\n/g, "↵\n");
            // If it's just space, don't show an explicit symbol so it spreads out normally,
            // or show a dot for debugging
            if (tVal === " ") tVal = " "; 
        }
        
        el.textContent = tVal;
        el.setAttribute("data-tooltip", `Type: ${tok.type} | Pos: Ln ${tok.line}, Col ${tok.column}`);
        tokensContainer.appendChild(el);
    });
}