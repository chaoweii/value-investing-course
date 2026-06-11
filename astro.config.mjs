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
        { label: 'Macro Backbone · Price Of Money', items: [
          { label: 'Macro Backbone Overview', slug: 'macro' },
          { label: 'What A Treasury Yield Is', slug: 'macro/what-a-yield-is' },
          { label: 'What Moves Treasury Yields', slug: 'macro/what-moves-yields' },
          { label: 'How Yields Reach Investments', slug: 'macro/how-yields-reach-investments' },
          { label: 'How Value Investors Use Yields', slug: 'macro/how-value-investors-use-yields' },
          { label: 'Rate Transmission Decision Lab', slug: 'macro/rate-transmission-lab' },
        ]},
        { label: 'Phase 2 · Underwrite Returns', items: [
          { label: 'Valuation Roadmap', slug: 'core/underwriting-roadmap' },
          { label: 'DCF Anatomy', slug: 'core/dcf-anatomy' },
          { label: 'Normalize History', slug: 'core/normalize-history' },
          { label: 'Revenue Drivers', slug: 'core/revenue-drivers' },
          { label: 'Costs And Reinvestment', slug: 'core/costs-and-reinvestment' },
          { label: 'Owner FCF Per Share', slug: 'core/owner-fcf-per-share' },
          { label: 'Discount Rates', slug: 'core/discount-rates' },
          { label: 'Terminal Value', slug: 'core/terminal-value' },
          { label: 'Scenarios And Reverse DCF', slug: 'core/scenarios-and-reverse-dcf' },
          { label: 'Full TOST DCF Build Lab', slug: 'core/tost-dcf-lab' },
          { label: 'ADYEY And BRK.B Contrasts', slug: 'core/dcf-contrast-cases' },
          { label: 'Revisit The Opening Decisions', slug: 'core/revisit-opening-decisions' },
        ]},
        { label: 'Phase 3 · Comparative Cases', items: [
          { label: 'Deep-Dive Case Library', slug: 'deep-dives' },
        ]},
        { label: 'Phase 4 · Construct The Portfolio', items: [
          { label: 'Portfolio Construction Overview', slug: 'portfolio' },
          { label: 'Stacking Asymmetry', slug: 'portfolio/stacking-asymmetry' },
          { label: 'Six Sizing Frameworks', slug: 'portfolio/sizing-frameworks' },
          { label: 'Correlation And Ruin', slug: 'portfolio/correlation-and-ruin' },
          { label: 'Long-Term Holding', slug: 'portfolio/long-term-holding' },
          { label: 'Live Portfolio Lab', slug: 'portfolio/live-lab' },
        ]},
        { label: 'Personal Journal', items: [
          { label: 'Decision Journal Guide', slug: 'journal' },
        ]},
      ],
    }),
  ],
});
