with open('frontend/pages/mock-interview.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'interview-stage' in l or 'stage-main-workspace' in l or 'workspace-spotlight-pane' in l or 'tile-interviewer' in l:
        print(f'{i+1}: {l.strip()[:100]}')

