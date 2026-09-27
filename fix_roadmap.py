import re

with open('/Users/venny/Downloads/careercompass-ai/static/roadmap.html', 'r') as f:
    content = f.read()

# 1. Remove Alex Rivera header block
alex_pattern = re.compile(r'<div class="flex items-center gap-md">\s*<div class="flex flex-col items-end">.*?<span class="text-label-md font-label-md font-bold">Alex Rivera</span>.*?</div>\s*</div>', re.IGNORECASE | re.DOTALL)
content = alex_pattern.sub('', content)

# 2. Remove Total Progress
progress_pattern = re.compile(r'<div class="text-right">\s*<p class="text-label-sm font-label-sm text-on-surface-variant uppercase tracking-wider mb-1">Total Progress</p>.*?</div>\s*</section>', re.IGNORECASE | re.DOTALL)
content = progress_pattern.sub('</section>', content)

# 3. Replace the Vertical Timeline with a dynamic AI container
timeline_pattern = re.compile(r'<!-- Vertical Timeline -->.*?</div>\s*<!-- Dashboard Analytics Preview -->', re.IGNORECASE | re.DOTALL)

dynamic_timeline = """<!-- AI Generated Roadmap -->
    <div id="ai-roadmap-loader" class="hidden flex-col items-center justify-center p-xl gap-md">
      <span class="material-symbols-outlined animate-spin text-primary" style="font-size: 48px;">cycle</span>
      <p class="text-body-lg text-on-surface-variant">Generating personalized roadmap using AI...</p>
    </div>
    <div id="ai-roadmap-container" class="relative pl-8 md:pl-16 space-y-xl">
      <div class="p-xl bg-surface-container-low border border-outline-variant rounded-xl text-center">
        <p class="text-body-lg text-on-surface-variant mb-4">You have not generated an AI Roadmap yet.</p>
        <button onclick="generateRoadmap()" class="bg-primary text-on-primary px-lg py-3 rounded-xl font-bold hover:brightness-95 transition-all">Generate My Roadmap</button>
      </div>
    </div>
    
    <script>
      async function generateRoadmap() {
          const role = localStorage.getItem('quizRole');
          const gapsStr = localStorage.getItem('quizGaps');
          if (!role || !gapsStr) {
              alert('Please take the AI Quiz first to generate a personalized roadmap!');
              window.location.href = 'quiz.html';
              return;
          }
          const gaps = JSON.parse(gapsStr);

          document.getElementById('ai-roadmap-loader').classList.remove('hidden');
          document.getElementById('ai-roadmap-loader').classList.add('flex');
          document.getElementById('ai-roadmap-container').classList.add('hidden');

          try {
              const res = await fetch('/api/roadmap/generate', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ role, gaps })
              });
              if (!res.ok) throw new Error('Failed to generate roadmap');
              const data = await res.json();
              
              const container = document.getElementById('ai-roadmap-container');
              container.innerHTML = '<div class="absolute left-[23px] md:left-[31px] top-4 bottom-4 w-1 roadmap-line rounded-full opacity-30"></div>';

              if (data.roadmap && data.roadmap.length > 0) {
                  data.roadmap.forEach((step, index) => {
                      const div = document.createElement('div');
                      div.className = "relative group";
                      div.innerHTML = `
                        <div class="absolute -left-[33px] md:-left-[41px] top-1 w-6 h-6 rounded-full bg-surface-container-lowest border-4 border-primary z-10"></div>
                        <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-md hover:border-primary/50 transition-colors">
                          <div class="flex justify-between items-start mb-2">
                            <span class="px-3 py-1 bg-surface-container-high text-on-surface-variant rounded-full text-label-sm font-label-sm">Step ${index + 1}</span>
                          </div>
                          <h4 class="text-headline-sm font-headline-sm text-on-surface mb-1">${step.title}</h4>
                          <p class="text-body-md font-body-md text-on-surface-variant">${step.description}</p>
                        </div>
                      `;
                      container.appendChild(div);
                  });
              } else {
                  container.innerHTML = '<p class="text-body-lg">No roadmap steps found.</p>';
              }
              
              document.getElementById('ai-roadmap-loader').classList.add('hidden');
              document.getElementById('ai-roadmap-loader').classList.remove('flex');
              container.classList.remove('hidden');

          } catch (err) {
              alert(err.message);
              document.getElementById('ai-roadmap-loader').classList.add('hidden');
              document.getElementById('ai-roadmap-loader').classList.remove('flex');
              document.getElementById('ai-roadmap-container').classList.remove('hidden');
          }
      }
    </script>
    <!-- Dashboard Analytics Preview -->"""

content = timeline_pattern.sub(dynamic_timeline, content)

with open('/Users/venny/Downloads/careercompass-ai/static/roadmap.html', 'w') as f:
    f.write(content)

print("roadmap.html updated")
