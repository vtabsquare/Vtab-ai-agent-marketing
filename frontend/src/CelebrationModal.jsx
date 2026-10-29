import React from 'react';
import { Icon } from './Bots.jsx';

export function CelebrationModal({ campaign, onClose, onView }) {
  if (!campaign) return null;
  const destinations = campaign.brief?.destinations?.length 
    ? campaign.brief.destinations 
    : ['instagram', 'facebook', 'whatsapp'];

  return (
    <div className="celebration-overlay" onClick={onClose}>
      <div className="celebration-card" onClick={e => e.stopPropagation()}>
        <button className="celebration-close" onClick={onClose} aria-label="Close">
          <Icon name="close" size={16} />
        </button>

        <div className="celebration-sparkle">🎉</div>
        <div className="celebration-kicker">PILOT SANDBOX BROADCAST SUCCESSFUL</div>
        <h2 className="celebration-title">Your Campaign Is Live!</h2>
        <p className="celebration-subtitle">
          Autonomous agents have completed research, creative generation, copy variants, and simulated live dispatch.
        </p>

        <div className="celebration-channels">
          {destinations.map(dest => {
            const label = dest === 'instagram' ? 'Instagram (@vtabsquare)'
              : dest === 'facebook' ? 'Facebook Page (Vtab Square)'
              : dest === 'whatsapp' ? 'WhatsApp Cloud Broadcast'
              : dest === 'discord' ? 'Discord Community Webhook'
              : dest === 'linkedin' ? 'LinkedIn Company Page'
              : dest === 'twitter' ? 'X / Twitter Feed' : dest;

            return (
              <div key={dest} className="celebration-channel-row">
                <div className="channel-icon-pill">
                  <span className="live-pulsing-check">✓</span>
                </div>
                <div className="channel-meta">
                  <b>{label}</b>
                  <small>Status: Live Published · 0 Discrepancies</small>
                </div>
                <span className="channel-live-tag">LIVE</span>
              </div>
            );
          })}
        </div>

        <div className="celebration-fidelity">
          <Icon name="shield" size={16} />
          <span><b>Brand Guardian Verdict:</b> 100% Price & Factual Fidelity Approved.</span>
        </div>

        <div className="celebration-actions">
          <button type="button" className="button primary full" onClick={() => { onView(campaign); onClose(); }}>
            View Campaign Details & Brand Card
          </button>
          <a
            href="https://www.vtabsquare.com"
            target="_blank"
            rel="noreferrer"
            className="celebration-enterprise-link"
          >
            Deploy This Engine For Your Business ↗
          </a>
        </div>
      </div>
    </div>
  );
}
