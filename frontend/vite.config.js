import { resolve } from 'path';
import { defineConfig } from 'vite';

const routeRewritesPlugin = () => ({
  name: 'route-rewrites-plugin',
  configureServer(server) {
    server.middlewares.use((req, res, next) => {
      const parts = req.url.split('?');
      const pathname = parts[0].replace(/\/+$/, '') || '/';
      const search = parts[1] ? '?' + parts[1] : '';

      const routeMap = {
        '/mock-interview': '/pages/mock-interview.html',
        '/mock-interview.html': '/pages/mock-interview.html',
        '/pages/mock-interview': '/pages/mock-interview.html',
        '/practice': '/pages/mock-interview.html',
        '/practice.html': '/pages/mock-interview.html',
        '/pages/practice': '/pages/mock-interview.html',
        '/interview': '/pages/mock-interview.html',
        '/interview.html': '/pages/mock-interview.html',
        '/pages/interview': '/pages/mock-interview.html',
        '/start-interview': '/pages/mock-interview.html',
        '/start-interview.html': '/pages/mock-interview.html',
        '/start': '/pages/mock-interview.html',
        '/dashboard': '/pages/dashboard.html',
        '/dashboard.html': '/pages/dashboard.html',
        '/pages/dashboard': '/pages/dashboard.html',
        '/auth': '/pages/auth.html',
        '/login': '/pages/auth.html',
        '/pages/auth': '/pages/auth.html',
        '/resume': '/pages/resume.html',
        '/pages/resume': '/pages/resume.html',
        '/assessment': '/pages/assessment.html',
        '/pages/assessment': '/pages/assessment.html',
        '/history': '/pages/history.html',
        '/report': '/pages/report.html',
        '/prep-plan': '/pages/prep-plan.html',
        '/voice-interviews': '/pages/voice-interviews.html',
        '/resume-review': '/pages/resume-review.html',
        '/question-banks': '/pages/question-banks.html',
        '/rubrics-scoring': '/pages/rubrics-scoring.html',
        '/coding-assignments': '/pages/coding-assignments.html',
        '/performance-reports': '/pages/performance-reports.html',
        '/accent-agnostic': '/pages/accent-agnostic.html',
        '/zero-retention': '/pages/zero-retention.html',
        '/end-to-end': '/pages/end-to-end.html',
        '/settings': '/pages/settings.html',
      };

      if (routeMap[pathname]) {
        req.url = routeMap[pathname] + search;
      }
      next();
    });
  },
  configurePreviewServer(server) {
    server.middlewares.use((req, res, next) => {
      const parts = req.url.split('?');
      const pathname = parts[0].replace(/\/+$/, '') || '/';
      const search = parts[1] ? '?' + parts[1] : '';

      const routeMap = {
        '/mock-interview': '/pages/mock-interview.html',
        '/mock-interview.html': '/pages/mock-interview.html',
        '/pages/mock-interview': '/pages/mock-interview.html',
        '/practice': '/pages/mock-interview.html',
        '/practice.html': '/pages/mock-interview.html',
        '/interview': '/pages/mock-interview.html',
        '/interview.html': '/pages/mock-interview.html',
        '/start-interview': '/pages/mock-interview.html',
        '/start-interview.html': '/pages/mock-interview.html',
        '/dashboard': '/pages/dashboard.html',
        '/auth': '/pages/auth.html',
        '/login': '/pages/auth.html',
        '/resume': '/pages/resume.html',
        '/assessment': '/pages/assessment.html',
      };

      if (routeMap[pathname]) {
        req.url = routeMap[pathname] + search;
      }
      next();
    });
  }
});

export default defineConfig({
  root: '.',
  plugins: [routeRewritesPlugin()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        mockInterviewRoot: resolve(__dirname, 'mock-interview.html'),
        practiceRoot: resolve(__dirname, 'practice.html'),
        auth: resolve(__dirname, 'pages/auth.html'),
        dashboard: resolve(__dirname, 'pages/dashboard.html'),
        mockInterview: resolve(__dirname, 'pages/mock-interview.html'),
        assessment: resolve(__dirname, 'pages/assessment.html'),
        history: resolve(__dirname, 'pages/history.html'),
        report: resolve(__dirname, 'pages/report.html'),
        resume: resolve(__dirname, 'pages/resume.html'),
        prepPlan: resolve(__dirname, 'pages/prep-plan.html'),
        voiceInterviews: resolve(__dirname, 'pages/voice-interviews.html'),
        resumeReview: resolve(__dirname, 'pages/resume-review.html'),
        questionBanks: resolve(__dirname, 'pages/question-banks.html'),
        rubricsScoring: resolve(__dirname, 'pages/rubrics-scoring.html'),
        codingAssignments: resolve(__dirname, 'pages/coding-assignments.html'),
        performanceReports: resolve(__dirname, 'pages/performance-reports.html'),
        accentAgnostic: resolve(__dirname, 'pages/accent-agnostic.html'),
        zeroRetention: resolve(__dirname, 'pages/zero-retention.html'),
        endToEnd: resolve(__dirname, 'pages/end-to-end.html'),
        settings: resolve(__dirname, 'pages/settings.html'),
      },
    },
  },
});
