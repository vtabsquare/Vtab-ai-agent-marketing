import React from 'react';
import { Icon } from './Bots.jsx';

export function PilotDemoEndModal({ campaign, onClose }) {
  if (!campaign) return null;
  const dest = campaign.brief?.destinations?.length
    ? campaign.brief.destinations
    : ['instagram', 'facebook', 'whatsapp'];

  const platformLabels = {
    instagram: 'Instagram', facebook: 'Facebook', whatsapp: 'WhatsApp',
    linkedin: 'LinkedIn', discord: 'Discord', twitter: 'X / Twitter'
  };

  return (
    <div className="pilot-end-overlay" onClick={onClose}>
      <div className="pilot-end-card" onClick={e => e.stopPropagation()}>
        <button className="pilot-end-close" onClick={onClose} aria-label="Close">
          <Icon name="close" size={16} />
        </button>

        {/* Top Badge */}
        <div className="pilot-end-badge">✦ PILOT DEMO COMPLETE</div>

        {/* Hero Headline */}
        <div className="pilot-end-rocket">🚀</div>
        <h2 className="pilot-end-title">
          Your AI campaign<br />just went live.
        </h2>
        <p className="pilot-end-subtitle">
          10 autonomous bots — research, strategy, creative, brand verification, multi-channel publishing — all finished in under 6 seconds. This was the <strong>sandbox preview</strong>.
        </p>

        {/* Campaign Summary Strip */}
        <div className="pilot-end-summary">
          <div className="pilot-end-summary-row">
            <span className="pilot-end-label">Campaign</span>
            <span className="pilot-end-value">{campaign.brief?.title || 'Your Campaign'}</span>
          </div>
          <div className="pilot-end-summary-row">
            <span className="pilot-end-label">Channels</span>
            <span className="pilot-end-value">{dest.map(d => platformLabels[d] || d).join(' · ')}</span>
          </div>
          <div className="pilot-end-summary-row">
            <span className="pilot-end-label">Bots Deployed</span>
            <span className="pilot-end-value">10/10 Synchronized ✓</span>
          </div>
          <div className="pilot-end-summary-row">
            <span className="pilot-end-label">Brand Fidelity</span>
            <span className="pilot-end-value">100% Verified ✓</span>
          </div>
        </div>

        {/* What's Unlocked in Full */}
        <div className="pilot-end-features">
          <div className="pilot-end-features-title">What you unlock with the full engine:</div>
          <div className="pilot-end-feature-grid">
            <div className="pilot-end-feature-item">
              <span className="pilot-end-feature-icon">⚡</span>
              <div>
                <b>Live Multi-Channel Publishing</b>
                <small>Instagram, Facebook, WhatsApp, LinkedIn — real posts, real audience</small>
              </div>
            </div>
            <div className="pilot-end-feature-item">
              <span className="pilot-end-feature-icon">🎯</span>
              <div>
                <b>Always-on AI Brand Guardian</b>
                <small>Zero hallucinations. Every claim fact-checked before dispatch.</small>
              </div>
            </div>
            <div className="pilot-end-feature-item">
              <span className="pilot-end-feature-icon">📊</span>
              <div>
                <b>Real-time Analytics & Optimization</b>
                <small>CTR, engagement, and conversion tracked with autonomous tuning.</small>
              </div>
            </div>
            <div className="pilot-end-feature-item">
              <span className="pilot-end-feature-icon">💬</span>
              <div>
                <b>AI Community Inbox</b>
                <small>Auto-draft replies for every comment across all your platforms.</small>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="pilot-end-cta-section">
          <p className="pilot-end-cta-tagline">
            Ready to run this for <em>your</em> brand — for real?
          </p>
          <a
            href="https://www.vtabsquare.com"
            target="_blank"
            rel="noreferrer"
            className="pilot-end-cta-btn"
          >
            🔥 Book Enterprise Access — It's Free
          </a>
          <a
            href="mailto:contact@vtabsquare.com?subject=AI Marketing Engine Enterprise Inquiry"
            className="pilot-end-contact-link"
          >
            Or email us at contact@vtabsquare.com ↗
          </a>
        </div>

        <p className="pilot-end-footer">
          Vtab Square · Autonomous Marketing OS · <a href="https://www.vtabsquare.com" target="_blank" rel="noreferrer">vtabsquare.com</a>
        </p>
      </div>
    </div>
  );
}
