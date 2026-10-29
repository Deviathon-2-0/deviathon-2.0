import { resolve } from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
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
      },
    },
  },
});
