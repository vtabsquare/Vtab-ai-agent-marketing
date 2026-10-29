import React from 'react';
import { Icon } from './Bots.jsx';

export function PilotDemoEndModal({ campaign, onClose, onView }) {
  if (!campaign) return null;
  const dest = campaign.brief?.destinations?.length
    ? campaign.brief.destinations
    : ['instagram', 'facebook', 'whatsapp'];

  const platformLabels = {
    instagram: 'Instagram',
    facebook: 'Facebook',
    whatsapp: 'WhatsApp',
    linkedin: 'LinkedIn',
    discord: 'Discord',
    twitter: 'X / Twitter'
  };

  return (
    <div className="pilot-end-overlay" onClick={onClose}>
      <div className="pilot-end-card" onClick={e => e.stopPropagation()}>
        <button className="pilot-end-close" onClick={onClose} aria-label="Close">
          <Icon name="close" size={16} />
        </button>

        {/* Top Badge */}
        <div className="pilot-end-badge">✦ PILOT DEMO COMPLETED</div>

        {/* Hero Headline */}
        <div className="pilot-end-rocket">🚀</div>
        <h2 className="pilot-end-title">
          Demo Ended · Contact For More
        </h2>
        <p className="pilot-end-subtitle">
          Your campaign was synthesized, verified, and simulated live across all channels! <strong>10 autonomous AI agents</strong> coordinated research, copy, creative design, and live publishing in seconds.
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
            <span className="pilot-end-value" style={{ color: '#38bdf8' }}>10/10 AI Agents Synchronized ✓</span>
          </div>
          <div className="pilot-end-summary-row">
            <span className="pilot-end-label">Brand Guardian</span>
            <span className="pilot-end-value" style={{ color: '#34d399' }}>100% Price & Claim Fidelity ✓</span>
          </div>
        </div>

        {/* CTA Section */}
        <div className="pilot-end-cta-section">
          <p className="pilot-end-cta-tagline">
            Ready to deploy autonomous AI marketing for <em>your business</em>?
          </p>
          <a
            href="https://www.vtabsquare.com"
            target="_blank"
            rel="noreferrer"
            className="pilot-end-cta-btn"
          >
            🔥 Deploy This Engine — Book Enterprise Access
          </a>
          
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center', marginTop: 10 }}>
            <a
              href="mailto:contact@vtabsquare.com?subject=Enterprise Inquiry: AI Marketing Manager Engine"
              className="pilot-end-contact-pill"
            >
              ✉️ Email Us (contact@vtabsquare.com)
            </a>
            <a
              href="https://wa.me/919840211234?text=Hi%20Vtab%20Square%2C%20I%20tested%20your%20AI%20Marketing%20Manager%20Pilot%20Demo%20and%20would%20like%20to%20learn%20more."
              target="_blank"
              rel="noreferrer"
              className="pilot-end-contact-pill"
              style={{ borderColor: '#25d366', color: '#86efac' }}
            >
              💬 Chat on WhatsApp
            </a>
          </div>
        </div>

        <div style={{ marginTop: 16 }}>
          <button
            type="button"
            className="button ghost full"
            style={{ color: '#94a3b8', fontSize: 13 }}
            onClick={() => {
              if (onView) onView(campaign);
              onClose();
            }}
          >
            View Completed Campaign & Creative Assets →
          </button>
        </div>

        <p className="pilot-end-footer" style={{ marginTop: 14 }}>
          Vtab Square · Autonomous Marketing OS · <a href="https://www.vtabsquare.com" target="_blank" rel="noreferrer">vtabsquare.com</a>
        </p>
      </div>
    </div>
  );
}
