import React, { useState, useMemo } from 'react';
import { Bot, Icon } from './Bots.jsx';

// Channel metadata and brand styling
const CHANNELS = [
  { id: 'all', label: 'All Channels', icon: 'grid', color: '#111827' },
  { id: 'instagram', label: 'Instagram Engagement', icon: 'instagram', color: '#c13584', brandGradient: true },
  { id: 'facebook', label: 'Facebook Engagement', icon: 'facebook', color: '#1877f2' },
  { id: 'whatsapp', label: 'WhatsApp Engagement', icon: 'whatsapp', color: '#16a34a' },
  { id: 'discord', label: 'Discord Engagement', icon: 'discord', color: '#5865f2' },
  { id: 'linkedin', label: 'LinkedIn Engagement', icon: 'linkedin', color: '#0a66c2' },
  { id: 'twitter', label: 'X / Twitter Engagement', icon: 'twitter', color: '#1da1f2' }
];

// High-fidelity social icons
function ChannelIcon({ channel, size = 16 }) {
  if (channel === 'facebook') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
    );
  }
  if (channel === 'instagram') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
      </svg>
    );
  }
  if (channel === 'whatsapp') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>
      </svg>
    );
  }
  if (channel === 'discord') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994.021-.041.001-.09-.041-.106a13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.929 1.793 8.18 1.793 12.061 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.894.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.028zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
      </svg>
    );
  }
  if (channel === 'linkedin') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 8.76a1.64 1.64 0 1 0 0-3.28 1.64 1.64 0 0 0 0 3.28m1.4 9.74v-8.37H5.06v8.37h2.8z"/>
      </svg>
    );
  }
  if (channel === 'twitter') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    );
  }
  return <Icon name="grid" size={size} />;
}

export function CommunityInbox({ community = [], api, act, busy, setNotice, setError }) {
  const [selectedChannel, setSelectedChannel] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedId, setCopiedId] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);

  // Calculate channel-specific counts and alerts
  const channelStats = useMemo(() => {
    const stats = {};
    CHANNELS.forEach(c => {
      const items = c.id === 'all' 
        ? community 
        : community.filter(item => (item.platform || '').toLowerCase() === c.id);
      const pending = items.filter(item => item.state === 'AWAITING_APPROVAL').length;
      stats[c.id] = { total: items.length, pending };
    });
    return stats;
  }, [community]);

  // Executive overview metrics
  const totalCount = community.length;
  const pendingCount = community.filter(item => item.state === 'AWAITING_APPROVAL').length;
  const approvedCount = community.filter(item => item.state === 'APPROVED').length;
  const activeChannelsCount = new Set(community.map(item => (item.platform || '').toLowerCase())).size;

  // Filtered list
  const filteredComments = useMemo(() => {
    return community.filter(item => {
      // 1. Channel filter
      if (selectedChannel !== 'all') {
        if ((item.platform || '').toLowerCase() !== selectedChannel) return false;
      }
      // 2. Status filter
      if (statusFilter === 'awaiting' && item.state !== 'AWAITING_APPROVAL') return false;
      if (statusFilter === 'approved' && item.state !== 'APPROVED') return false;
      if (statusFilter === 'rejected' && item.state !== 'REJECTED') return false;
      // 3. Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const authorMatch = (item.author || '').toLowerCase().includes(q);
        const textMatch = (item.text || '').toLowerCase().includes(q);
        const replyMatch = (item.output?.draft_reply || '').toLowerCase().includes(q);
        const categoryMatch = (item.output?.category || '').toLowerCase().includes(q);
        if (!authorMatch && !textMatch && !replyMatch && !categoryMatch) return false;
      }
      return true;
    });
  }, [community, selectedChannel, statusFilter, searchQuery]);

  // Sync action handler
  async function handleSync() {
    setIsSyncing(true);
    await act(async () => {
      try {
        const r = await api('/engagement/sync', 'POST');
        setNotice(`Synced social comments. ${r.queued} new comments found.`);
      } catch (err) {
        if (setError) setError(err.message);
      } finally {
        setIsSyncing(false);
      }
    });
  }

  // Copy reply text
  function handleCopy(id, text) {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  }

  // Format timestamp helper
  function formatTime(timestamp) {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp * 1000);
      const now = new Date();
      const diffMs = now - date;
      const diffMin = Math.round(diffMs / 60000);
      if (diffMin < 1) return 'Just now';
      if (diffMin < 60) return `${diffMin}m ago`;
      const diffHours = Math.round(diffMin / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  }

  return (
    <div className="community-container">
      {/* Header */}
      <header className="community-header">
        <div className="community-title-area">
          <div className="kicker">LISTEN. UNDERSTAND. RESPOND.</div>
          <h1>Community & Engagement Hub</h1>
          <p>
            Monitor customer conversations across social channels. Review AI-synthesized response drafts, customize copy, and post with one-click executive sign-off.
          </p>
        </div>
        <div className="community-actions">
          <button
            type="button"
            className="sync-button"
            disabled={busy || isSyncing}
            onClick={handleSync}
          >
            <span className={`sync-icon ${isSyncing ? 'spinning' : ''}`}>
              <Icon name="bolt" size={15} />
            </span>
            {isSyncing ? 'Syncing Feeds…' : 'Sync Social Comments'}
          </button>
        </div>
      </header>

      {/* Top Metric Cards */}
      <section className="community-metrics-row">
        <div className="community-metric-card">
          <div className="metric-info">
            <h3>Total Engagements</h3>
            <div className="metric-num">{totalCount}</div>
          </div>
          <div className="metric-badge-icon purple">
            <Icon name="chat" size={22} />
          </div>
        </div>

        <div className="community-metric-card">
          <div className="metric-info">
            <h3>Needs Review</h3>
            <div className="metric-num" style={{ color: pendingCount > 0 ? '#d97706' : '#111827' }}>
              {pendingCount}
            </div>
          </div>
          <div className="metric-badge-icon amber">
            <Icon name="bell" size={22} />
          </div>
        </div>

        <div className="community-metric-card">
          <div className="metric-info">
            <h3>Approved & Replied</h3>
            <div className="metric-num" style={{ color: '#059669' }}>
              {approvedCount}
            </div>
          </div>
          <div className="metric-badge-icon emerald">
            <Icon name="check" size={22} />
          </div>
        </div>

        <div className="community-metric-card">
          <div className="metric-info">
            <h3>Active Channels</h3>
            <div className="metric-num">{activeChannelsCount || '0'}</div>
          </div>
          <div className="metric-badge-icon blue">
            <Icon name="link" size={22} />
          </div>
        </div>
      </section>

      {/* Navigation & Channel Segmented Tabs */}
      <nav className="community-nav-bar">
        <div className="channel-tabs">
          {CHANNELS.map(ch => {
            const count = channelStats[ch.id]?.total || 0;
            const hasPending = (channelStats[ch.id]?.pending || 0) > 0;
            const isActive = selectedChannel === ch.id;

            return (
              <button
                key={ch.id}
                type="button"
                className={`channel-tab ${isActive ? 'active' : ''}`}
                onClick={() => setSelectedChannel(ch.id)}
              >
                <ChannelIcon channel={ch.id} size={15} />
                <span>{ch.label}</span>
                <span className="tab-count">{count}</span>
                {hasPending && <span className="urgent-dot" title="Action required: pending draft" />}
              </button>
            );
          })}
        </div>

        {/* Secondary Filter & Search */}
        <div className="secondary-filter-bar">
          <div className="status-pills">
            {[
              { id: 'all', label: `All (${channelStats[selectedChannel]?.total || 0})` },
              { id: 'awaiting', label: `Needs Review (${channelStats[selectedChannel]?.pending || 0})` },
              { id: 'approved', label: 'Approved & Replied' },
              { id: 'rejected', label: 'Rejected' }
            ].map(pill => (
              <button
                key={pill.id}
                type="button"
                className={`status-pill ${statusFilter === pill.id ? 'active' : ''}`}
                onClick={() => setStatusFilter(pill.id)}
              >
                {pill.label}
              </button>
            ))}
          </div>

          <div className="search-box">
            <span className="search-icon-svg">
              <Icon name="search" size={15} />
            </span>
            <input
              type="text"
              placeholder="Search comments, authors or replies…"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </nav>

      {/* Comments List */}
      <div className="engagement-grid">
        {filteredComments.length > 0 ? (
          filteredComments.map(item => {
            const platformKey = (item.platform || 'generic').toLowerCase();
            const isAwaiting = item.state === 'AWAITING_APPROVAL';
            const isApproved = item.state === 'APPROVED';
            const isRejected = item.state === 'REJECTED';
            const initials = (item.author || 'User')
              .split(' ')
              .map(n => n[0])
              .join('')
              .toUpperCase()
              .slice(0, 2);

            return (
              <article
                key={item.id}
                className={`engagement-card ${
                  isAwaiting ? 'status-awaiting' : isApproved ? 'status-approved' : isRejected ? 'status-rejected' : ''
                }`}
              >
                <div>
                  {/* Top Bar: Platform & State */}
                  <div className="card-top-bar">
                    <span className={`platform-chip ${platformKey}`}>
                      <ChannelIcon channel={platformKey} size={13} />
                      {item.platform || 'Unknown'}
                    </span>

                    <span
                      className={`status-badge ${
                        isAwaiting
                          ? 'awaiting'
                          : isApproved
                          ? 'approved'
                          : isRejected
                          ? 'rejected'
                          : 'queued'
                      }`}
                    >
                      {isAwaiting && <span className="urgent-dot" />}
                      {isAwaiting
                        ? 'Needs Approval'
                        : isApproved
                        ? 'Approved & Delivered'
                        : isRejected
                        ? 'Draft Rejected'
                        : item.state.replaceAll('_', ' ')}
                    </span>
                  </div>

                  {/* Author Meta */}
                  <div className="author-profile-row">
                    <div className="author-avatar">{initials}</div>
                    <div className="author-meta">
                      <h4 className="author-name">{item.author || 'Social Audience Member'}</h4>
                      <div className="author-subtext">
                        <span>{formatTime(item.created_at)}</span>
                        {item.post_id && (
                          <>
                            <span>•</span>
                            <span className="post-ref-tag" title={item.post_id}>
                              Post #{item.post_id.slice(-8)}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Customer Comment Bubble */}
                  <div className="comment-bubble-container">
                    {item.output?.category && (
                      <span className="inquiry-tag">{item.output.category}</span>
                    )}
                    <div className="comment-bubble">"{item.text}"</div>
                  </div>

                  {/* AI Suggested Reply */}
                  {item.output?.draft_reply && (
                    <div className="ai-reply-container">
                      <div className="ai-reply-header">
                        <span className="ai-reply-label">
                          <Bot role="engagement" size={20} />
                          AI Suggested Reply
                        </span>
                        <button
                          type="button"
                          className="copy-button"
                          onClick={() => handleCopy(item.id, item.output.draft_reply)}
                        >
                          {copiedId === item.id ? '✓ Copied' : 'Copy'}
                        </button>
                      </div>
                      <p className="ai-reply-text">{item.output.draft_reply}</p>
                    </div>
                  )}

                  {item.error && <p role="alert" className="help" style={{ color: '#ef4444' }}>{item.error}</p>}
                </div>

                {/* Card Actions & Delivery Status Footer */}
                <div className="card-actions-area">
                  {isAwaiting && (
                    <div className="action-buttons-row">
                      <button
                        type="button"
                        className="approve-btn"
                        disabled={busy}
                        onClick={() =>
                          act(() =>
                            api('/engagement/' + item.id + '/decision', 'POST', {
                              draft_hash: item.draft_hash,
                              approve: true
                            })
                          )
                        }
                      >
                        <ChannelIcon channel={platformKey} size={15} />
                        {platformKey === 'facebook'
                          ? 'Approve & Post to Facebook'
                          : platformKey === 'instagram'
                          ? 'Approve & Post to Instagram'
                          : platformKey === 'whatsapp'
                          ? 'Approve & Send via WhatsApp'
                          : platformKey === 'discord'
                          ? 'Approve & Post to Discord'
                          : 'Approve & Post'}
                      </button>

                      <button
                        type="button"
                        className="reject-btn"
                        disabled={busy}
                        onClick={() =>
                          act(() =>
                            api('/engagement/' + item.id + '/decision', 'POST', {
                              draft_hash: item.draft_hash,
                              approve: false
                            })
                          )
                        }
                      >
                        Reject
                      </button>
                    </div>
                  )}

                  {isApproved && (
                    <>
                      {platformKey === 'facebook' && (
                        item.facebook_reply_posted ? (
                          <div className="delivery-notice success">
                            ✓ Reply posted to Facebook comment thread! (ID: {item.facebook_reply_id})
                          </div>
                        ) : item.facebook_reply_error ? (
                          <div className="delivery-notice error">
                            ⚠ Approved, but posting to Facebook failed: {item.facebook_reply_error}
                          </div>
                        ) : (
                          <div className="delivery-notice pending-notice">
                            Approved. Dispatching reply to Facebook thread…
                          </div>
                        )
                      )}

                      {platformKey === 'instagram' && (
                        item.instagram_reply_posted ? (
                          <div className="delivery-notice success">
                            ✓ Reply posted to Instagram comment thread! (ID: {item.instagram_reply_id})
                          </div>
                        ) : item.instagram_reply_error ? (
                          <div className="delivery-notice error">
                            ⚠ Approved, but posting to Instagram failed: {item.instagram_reply_error}
                          </div>
                        ) : (
                          <div className="delivery-notice pending-notice">
                            Approved. Dispatching reply to Instagram comment…
                          </div>
                        )
                      )}

                      {platformKey === 'whatsapp' && (
                        item.whatsapp_reply_posted ? (
                          <div className="delivery-notice success">
                            ✓ Message sent via WhatsApp Cloud API! (ID: {item.whatsapp_reply_id})
                          </div>
                        ) : item.whatsapp_reply_error ? (
                          <div className="delivery-notice error">
                            ⚠ Approved, but WhatsApp delivery failed: {item.whatsapp_reply_error}
                          </div>
                        ) : (
                          <div className="delivery-notice pending-notice">
                            Approved. Dispatching WhatsApp message…
                          </div>
                        )
                      )}

                      {!['facebook', 'instagram', 'whatsapp'].includes(platformKey) && (
                        <div className="delivery-notice success">
                          ✓ Approved for live delivery.
                        </div>
                      )}
                    </>
                  )}

                  {isRejected && (
                    <div className="delivery-notice rejected-notice">
                      ✕ Draft reply was rejected.
                    </div>
                  )}
                </div>
              </article>
            );
          })
        ) : (
          <section className="community-empty-state">
            <div className={`empty-icon-wrap ${selectedChannel}`}>
              <ChannelIcon channel={selectedChannel} size={36} />
            </div>
            <h2>
              {selectedChannel === 'all'
                ? 'No conversations found'
                : `No ${CHANNELS.find(c => c.id === selectedChannel)?.label || selectedChannel} yet`}
            </h2>
            <p>
              {searchQuery
                ? `No comments match "${searchQuery}". Try adjusting your keywords or clearing the filter.`
                : selectedChannel === 'all'
                ? 'Customer comments from your connected social handles (Facebook, Instagram, WhatsApp) will arrive here automatically.'
                : `When customers comment on your ${selectedChannel} posts or send inbound inquiries, Community Bot will draft answers and wait for your one-click approval.`}
            </p>
            <button
              type="button"
              className="sync-button"
              disabled={busy || isSyncing}
              onClick={handleSync}
            >
              <Icon name="bolt" size={15} />
              Sync Social Feeds Now
            </button>
          </section>
        )}
      </div>
    </div>
  );
}
