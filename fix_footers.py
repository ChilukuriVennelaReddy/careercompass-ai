import os
import glob

footer_search = """    <div class="flex gap-lg">
      <a class="text-label-sm font-label-sm text-on-surface-variant hover:text-primary transition-all" href="#">Privacy Policy</a>
      <a class="text-label-sm font-label-sm text-on-surface-variant hover:text-primary transition-all" href="#">Terms of Service</a>
      <a class="text-label-sm font-label-sm text-on-surface-variant hover:text-primary transition-all" href="#">Contact</a>
      <a class="text-label-sm font-label-sm text-on-surface-variant hover:text-primary transition-all" href="#">LinkedIn</a>
    </div>"""

footer_replace = """    <div class="flex gap-lg">
      <a class="text-label-sm font-label-sm text-on-surface-variant hover:text-primary transition-all cursor-pointer" onclick="showModal('Privacy Policy', 'Your privacy is our priority. CareerCompass AI collects data solely for personalized skill analysis and career recommendations. We do not sell or share your data with third parties. All interactions are secure and encrypted.')">Privacy Policy</a>
      <a class="text-label-sm font-label-sm text-on-surface-variant hover:text-primary transition-all cursor-pointer" onclick="showModal('Terms of Service', 'By using CareerCompass AI, you agree to our terms. This platform is designed for educational and career guidance purposes. AI-generated advice should be used as a supplementary tool. Users must not abuse the API or try to extract underlying models.')">Terms of Service</a>
      <a class="text-label-sm font-label-sm text-on-surface-variant hover:text-primary transition-all" href="mailto:vennelareddy1908@gmail.com">Contact</a>
    </div>"""

modal_code = """
<!-- Global Modal for Policies/Certs -->
<div id="global-modal" class="fixed inset-0 z-[100] hidden items-center justify-center bg-black/50 backdrop-blur-sm transition-opacity">
  <div class="bg-surface border border-outline-variant p-xl rounded-2xl max-w-lg w-full shadow-2xl transform transition-transform scale-95 opacity-0" id="global-modal-content">
    <div class="flex justify-between items-start mb-md">
      <h3 class="text-headline-sm font-headline-sm text-on-surface" id="modal-title">Title</h3>
      <button onclick="closeModal()" class="text-on-surface-variant hover:text-error transition-colors">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
    <div class="text-body-md text-on-surface-variant space-y-sm" id="modal-body">
      Content
    </div>
    <div class="mt-lg flex justify-end">
      <button onclick="closeModal()" class="bg-primary text-on-primary px-lg py-2 rounded-xl font-label-md hover:brightness-95 transition-all">Close</button>
    </div>
  </div>
</div>
<script>
  function showModal(title, content) {
      const modal = document.getElementById('global-modal');
      const modalContent = document.getElementById('global-modal-content');
      document.getElementById('modal-title').innerText = title;
      document.getElementById('modal-body').innerHTML = content;
      
      modal.classList.remove('hidden');
      modal.classList.add('flex');
      // small delay for transition
      setTimeout(() => {
          modalContent.classList.remove('scale-95', 'opacity-0');
          modalContent.classList.add('scale-100', 'opacity-100');
      }, 10);
  }
  function closeModal() {
      const modal = document.getElementById('global-modal');
      const modalContent = document.getElementById('global-modal-content');
      modalContent.classList.remove('scale-100', 'opacity-100');
      modalContent.classList.add('scale-95', 'opacity-0');
      setTimeout(() => {
          modal.classList.add('hidden');
          modal.classList.remove('flex');
      }, 200);
  }
</script>
</body>
"""

for file_path in glob.glob('/Users/venny/Downloads/careercompass-ai/static/*.html'):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # In index.html the classes might differ slightly due to hover states, so let's do regex or generic replace
    import re
    # Replace footer links
    pattern = re.compile(r'<div class="flex gap-lg">\s*<a[^>]*>Privacy Policy</a>\s*<a[^>]*>Terms of Service</a>\s*<a[^>]*>Contact</a>\s*<a[^>]*>LinkedIn</a>\s*</div>', re.IGNORECASE)
    content = pattern.sub(footer_replace, content)
    
    # Remove Alex Chen
    alex_chen_pattern = re.compile(r'<div class="hidden lg:block">\s*<div class="flex items-center gap-md bg-surface-container px-lg py-sm rounded-full">.*?Alex Chen.*?</p>\s*</div>\s*</div>\s*</div>', re.IGNORECASE | re.DOTALL)
    content = alex_chen_pattern.sub('', content)

    # Inject modal before </body> if not already there
    if 'id="global-modal"' not in content:
        content = content.replace('</body>', modal_code)

    with open(file_path, 'w') as f:
        f.write(content)

print("Footers, Alex Chen, and Modals updated.")
