import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  integrations: [
    starlight({
      title: 'Owner Mindset',
      description: 'A case-first apprenticeship in long-term value investing.',
      favicon: '/favicon.svg',
      customCss: ['./src/styles/custom.css'],
      sidebar: [
        { label: 'Start Here', items: [
          { label: 'Course Home', slug: '' },
          { label: 'How This Apprenticeship Works', slug: 'start/course-philosophy' },
          { label: 'Learning Roadmap', slug: 'start/roadmap' },
        ]},
        { label: 'Phase 0 · Decide First', items: [
          { label: 'Opening Decision Labs', slug: 'decision-labs' },
          { label: 'TOST · Product Love vs. Stock Value', slug: 'decision-labs/tost' },
          { label: 'ADYEY · Wonderful Business, Asymmetric Stock?', slug: 'decision-labs/adyey' },
          { label: 'BRK.B · The Opportunity-Cost Benchmark', slug: 'decision-labs/brkb' },
        ]},
        { label: 'Phase 1 · Own The Business', items: [
          { label: 'Lecture Roadmap', slug: 'core/business-owner-roadmap' },
        ]},
        { label: 'Phase 2 · Underwrite Returns', items: [
          { label: 'Valuation Roadmap', slug: 'core/underwriting-roadmap' },
          { label: 'Revisit The Opening Decisions', slug: 'core/revisit-opening-decisions' },
        ]},
        { label: 'Phase 3 · Comparative Cases', items: [
          { label: 'Deep-Dive Case Library', slug: 'deep-dives' },
        ]},
        { label: 'Personal Journal', items: [
          { label: 'Decision Journal Guide', slug: 'journal' },
        ]},
      ],
    }),
  ],
});
