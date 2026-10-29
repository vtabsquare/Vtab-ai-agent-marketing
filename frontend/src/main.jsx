import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Bot, Icon, BOTS, ROLES } from './Bots.jsx';
import { ControlCenter } from './ControlCenter.jsx';
import { CommunityInbox } from './CommunityInbox.jsx';
import { Login } from './Login.jsx';
import { PilotDemoEndModal } from './PilotDemoEndModal.jsx';
import {
  DEFAULT_PILOT_BRAND,
  INITIAL_PILOT_WORKFLOWS,
  INITIAL_PILOT_COMMUNITY,
  getPilotWorkflows,
  savePilotWorkflows,
  getPilotBrand,
  savePilotBrand,
  getPilotCommunity,
  savePilotCommunity,
  simulatePilotCampaign,
  completePilotCampaign,
  resetPilotSession,
  renderPilotSvg
} from './pilotData.js';
import './styles.css';
import './modern.css';
import './pilot-demo-end.css';
import { api } from './api.js';

const STATUS = {
  SCHEDULED_WAIT: 'Analytics in 24 hours',
  PENDING: 'Waiting for inputs',
  RUNNING: 'Working',
  ACCEPTED: 'Done',
  WAITING_INPUT: 'Needs your input',
  BLOCKED: 'Needs attention',
  RETRY_SCHEDULED: 'Retry scheduled',
  CANCELLED: 'Cancelled',
  QUEUED: 'Running',
  AWAITING_APPROVAL: 'Review needed',
  COMPLETED: 'Complete'
};

const EMPTY = { title: '', audience: '', goal: '', instructions: '', checkpoint: 'creative' };

const PILOT_DEFAULT_BRIEF = {
  title: 'Vtab Square Global AI Masterclass & Live Platform Demo',
  audience: 'Software developers, engineering leads, SaaS founders, and digital marketing teams',
  goal: 'Drive 500+ free registrations for the November 20th live virtual masterclass and generate developer community engagement',
  instructions: 'Highlight autonomous multi-agent coordination, peer code reviews, and emphasize that access is 100% free with no credit card required. Keep the visual aesthetic dark mode with neon indigo and electric blue accents.',
  checkpoint: 'none'
};

function App() {
  const [auth, setAuth] = useState(null);
  const isPilot = Boolean(
    auth?.user?.is_pilot ||
    window.location.pathname.includes('/demo') ||
    window.location.pathname.includes('/pilot') ||
    window.location.pathname.includes('/embed') ||
    window.location.search.includes('demo=') ||
    window.location.search.includes('pilot=') ||
    window.location.search.includes('embed=') ||
    (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('vtab_pilot_session') === '1')
  );

  const [pilotDemoEnd, setPilotDemoEnd] = useState(null);
  const [sessionCompletedCampaign, setSessionCompletedCampaign] = useState(null);
  const [settings, setSettings] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [connected, setConnected] = useState(true);
  const [attention, setAttention] = useState(null);
  const seenRequests = useRef(new Set());
  const loadedRequests = useRef(false);
  const shownAttentionId = useRef(null);
  const [community, setCommunity] = useState([]);
  const [page, setPage] = useState('workflows');
  const [selected, setSelected] = useState(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [brief, setBrief] = useState(() => {
    const isPilotInitial = typeof window !== 'undefined' && Boolean(
      window.location.pathname.includes('/demo') ||
      window.location.pathname.includes('/pilot') ||
      window.location.pathname.includes('/embed') ||
      window.location.search.includes('demo=') ||
      window.location.search.includes('pilot=') ||
      window.location.search.includes('embed=') ||
      (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('vtab_pilot_session') === '1')
    );
    return isPilotInitial ? { ...PILOT_DEFAULT_BRIEF } : { ...EMPTY };
  });
  const [tab, setTab] = useState('conversation');
  const [focusedBot, setFocusedBot] = useState(null);
  const [auditOpen, setAuditOpen] = useState(false);
  const [auditEvents, setAuditEvents] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);
  const [form, setForm] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [answers, setAnswers] = useState({});
  const [revision, setRevision] = useState('');
  const [inbox, setInbox] = useState(false);

  const effectiveWorkflows = isPilot ? getPilotWorkflows() : workflows;
  const effectiveCommunity = isPilot ? getPilotCommunity() : community;
  const effectiveNotifications = isPilot ? [] : notifications;

  const current = effectiveWorkflows.find(c => c.id === selected);
  const feedEnd = useRef(null);
  const feedBox = useRef(null);
  const follow = useRef(true);

  async function refresh(forcePilot) {
    const activePilot = typeof forcePilot === 'boolean' ? forcePilot : isPilot;
    if (activePilot) {
      let s;
      try {
        s = await api('/settings');
      } catch (e) {
        s = {
          provider: 'demo',
          ready: true,
          data_mode: 'pilot',
          deployment_mode: 'pilot',
          publishing_mode: 'simulation',
          brand: getPilotBrand(),
          platforms: ['instagram', 'facebook', 'whatsapp']
        };
      }
      s.brand = getPilotBrand();
      s.publishing_mode = 'simulation';
      s.ready = true;
      setSettings(s);
      setWorkflows(getPilotWorkflows());
      setCommunity(getPilotCommunity());
      setNotifications([]);
      setAttention(null);
      setConnected(true);
      return;
    }
    const [s, cs, ns, es] = await Promise.all([
      api('/settings'),
      api('/campaigns'),
      api('/notifications'),
      api('/engagement')
    ]);
    setCommunity(es);
    setSettings(s);
    setWorkflows(cs);
    setNotifications(ns);
    setConnected(true);
  }

  async function checkAuth() {
    const isPilotUrl = Boolean(
      window.location.pathname.includes('/demo') ||
      window.location.pathname.includes('/pilot') ||
      window.location.pathname.includes('/embed') ||
      window.location.search.includes('demo=') ||
      window.location.search.includes('pilot=') ||
      window.location.search.includes('embed=')
    );

    try {
      const res = await api('/auth/me');
      const pilotCheck = Boolean(res.user?.is_pilot || isPilotUrl);
      if (pilotCheck) {
        try { sessionStorage.setItem('vtab_pilot_session', '1'); } catch (e) {}
      }
      setAuth({
        authenticated: res.authenticated,
        user: pilotCheck
          ? {
              ...(res.user || {}),
              is_pilot: true,
              name: res.user?.name || 'Vtab Pilot Guest',
              email: res.user?.email || 'demo@vtabsquare.com'
            }
          : res.user
      });
      if (pilotCheck) {
        resetPilotSession();
        setBrief({ ...PILOT_DEFAULT_BRIEF });
      }
      if (res.authenticated) await refresh(pilotCheck);
    } catch (e) {
      if (isPilotUrl) {
        try {
          const r = await api('/auth/demo', 'POST');
          try { sessionStorage.setItem('vtab_pilot_session', '1'); } catch (err) {}
          resetPilotSession();
          setBrief({ ...PILOT_DEFAULT_BRIEF });
          setAuth({ authenticated: true, user: { ...r.user, is_pilot: true } });
          await refresh(true);
        } catch (err) {
          try { sessionStorage.setItem('vtab_pilot_session', '1'); } catch (err2) {}
          setAuth({
            authenticated: true,
            user: {
              id: 'pilot-guest',
              email: 'demo@vtabsquare.com',
              name: 'Vtab Pilot Guest',
              role: 'pilot',
              is_pilot: true
            }
          });
          await refresh(true);
        }
      } else {
        setAuth({ authenticated: false, user: null });
      }
    }
  }

  async function handleLogout() {
    try {
      await api('/auth/logout', 'POST');
    } catch (e) {}
    setAuth({ authenticated: false, user: null });
    setSettings(null);
    setWorkflows([]);
  }

  async function openAuditTrail() {
    if (isPilot) return;
    setAuditOpen(true);
    setAuditLoading(true);
    try {
      const list = await api('/audit?limit=100');
      setAuditEvents(list);
    } catch (e) {
      setError('Failed to load audit trail: ' + e.message);
    } finally {
      setAuditLoading(false);
    }
  }

  useEffect(() => {
    checkAuth();
    const timer = setInterval(() => {
      if (!document.hidden && !isPilot) {
        refresh().catch(e => {
          if (e.message && (e.message.includes('Sign in') || e.message.includes('401'))) {
            setAuth({ authenticated: false, user: null });
          } else {
            setConnected(false);
            setError(e.message);
          }
        });
      }
    }, 3500);

    const onVisible = () => {
      if (!document.hidden && !isPilot) {
        refresh().catch(e => {
          if (e.message && (e.message.includes('Sign in') || e.message.includes('401'))) {
            setAuth({ authenticated: false, user: null });
          } else {
            setConnected(false);
            setError(e.message);
          }
        });
      }
    };

    const onKey = (e) => {
      if (e.key === 'Escape') {
        setCreateOpen(false);
        setInbox(false);
        setAuditOpen(false);
      }
    };

    document.addEventListener('visibilitychange', onVisible);
    document.addEventListener('keydown', onKey);
    return () => {
      clearInterval(timer);
      document.removeEventListener('visibilitychange', onVisible);
      document.removeEventListener('keydown', onKey);
    };
  }, [isPilot]);

  useEffect(() => {
    setError('');
    setNotice('');
    follow.current = true;
  }, [page, selected]);

  useEffect(() => {
    if (tab === 'conversation' && follow.current && feedBox.current) {
      feedBox.current.scrollTop = feedBox.current.scrollHeight;
    }
  }, [current?.events?.length, tab, selected]);

  useEffect(() => {
    if (!settings || isPilot) return;
    const notifIds = new Set(notifications.map(q => q.id));
    const fresh = notifications.find(q => !seenRequests.current.has(q.id));
    notifications.forEach(q => seenRequests.current.add(q.id));
    if (loadedRequests.current && fresh && fresh.id !== shownAttentionId.current) {
      shownAttentionId.current = fresh.id;
      setAttention(fresh);
    }
    if (shownAttentionId.current && !notifIds.has(shownAttentionId.current)) {
      shownAttentionId.current = null;
      setAttention(null);
    }
    loadedRequests.current = true;
  }, [notifications, settings, isPilot]);

  async function act(fn) {
    setBusy(true);
    setError('');
    try {
      await fn();
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  function handlePilotApprove(campaignId) {
    const completed = completePilotCampaign(campaignId, () => {
      setWorkflows(getPilotWorkflows());
    });
    if (completed) {
      setWorkflows(getPilotWorkflows());
      setSelected(completed.id);
      setSessionCompletedCampaign({ ...completed });
      setTimeout(() => setPilotDemoEnd({ ...completed }), 300);
    }
  }

  function select(c) {
    if (isPilot && sessionCompletedCampaign && c.id !== sessionCompletedCampaign.id) {
      setPilotDemoEnd({ ...sessionCompletedCampaign });
      return;
    }
    setSelected(c.id);
    setPage('workflows');
    setInbox(false);
    setTab('conversation');
    setFocusedBot(null);
  }

  function newWorkflow() {
    if (isPilot && sessionCompletedCampaign) {
      setPilotDemoEnd({ ...sessionCompletedCampaign });
      return;
    }
    setCreateOpen(true);
    setBrief(isPilot ? { ...PILOT_DEFAULT_BRIEF } : { ...EMPTY });
    setError('');
  }

  function openSettings() {
    setPage('settings');
    const brand = isPilot ? getPilotBrand() : { ...settings.brand };
    setForm({
      ...settings,
      api_key: '',
      social_keys: {},
      brand
    });
  }

  function handleSaveBrandFacts() {
    if (isPilot) {
      savePilotBrand(form.brand);
      setNotice('Approved brand facts saved to Pilot Sandbox! Future workflows will use these facts.');
      setTimeout(() => setNotice(''), 3500);
    }
  }

  function handlePilotCommunityDecision(targetId, approve) {
    const list = getPilotCommunity();
    const updated = list.map(item => {
      if (item.id === targetId) {
        const copy = { ...item, state: approve ? 'APPROVED' : 'REJECTED' };
        if (approve) {
          if (copy.platform === 'facebook') {
            copy.facebook_reply_posted = true;
            copy.facebook_reply_id = 'sim_fb_rep_' + Math.random().toString(36).substr(2, 6);
          } else if (copy.platform === 'instagram') {
            copy.instagram_reply_posted = true;
            copy.instagram_reply_id = 'sim_ig_rep_' + Math.random().toString(36).substr(2, 6);
          } else if (copy.platform === 'whatsapp') {
            copy.whatsapp_reply_posted = true;
            copy.whatsapp_reply_id = 'sim_wa_msg_' + Math.random().toString(36).substr(2, 6);
          } else if (copy.platform === 'linkedin') {
            copy.linkedin_reply_posted = true;
            copy.linkedin_reply_id = 'sim_li_rep_' + Math.random().toString(36).substr(2, 6);
          }
        }
        return copy;
      }
      return item;
    });
    savePilotCommunity(updated);
    setCommunity(getPilotCommunity());
    setNotice(approve ? 'Simulated reply approved and dispatched!' : 'Simulated draft rejected.');
    setTimeout(() => setNotice(''), 3000);
  }

  const active = effectiveWorkflows.filter(c => !['COMPLETED', 'CANCELLED'].includes(c.state)).length;
  const completed = effectiveWorkflows.filter(c => c.state === 'COMPLETED').length;
  const openRequests = current?.input_requests?.filter(q => q.status === 'OPEN') || [];
  const blocked = current ? Object.entries(current.nodes || {}).filter(([r, n]) => n.state === 'BLOCKED') : [];
  const shownEvents = current?.events?.filter(e => !focusedBot || e.actor === focusedBot || e.target === focusedBot) || [];
  const running = current ? Object.entries(current.nodes || {}).filter(([r, n]) => n.state === 'RUNNING').map(([r]) => r) : [];

  if (auth === null) {
    return (
      <div className="opening">
        <Bot role="manager" size={70} />
        <h2>Opening your control room…</h2>
      </div>
    );
  }

  if (!auth.authenticated) {
    return <Login onLogin={u => { setAuth({ authenticated: true, user: u }); refresh(); }} />;
  }

  if (!settings) {
    return (
      <div className="opening">
        <Bot role="manager" size={70} />
        <h2>Loading workspace settings…</h2>
        {error && <p>{error}</p>}
      </div>
    );
  }

  if (page === 'platform') {
    return <ControlCenter settings={settings} onSaved={refresh} onBack={() => setPage('workflows')} />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="logo">
          <span><Icon name="bolt" size={25} /></span>
          <div>MARKETING OS<b>Agent workspace</b></div>
        </div>

        <div className="nav-label">WORKSPACE</div>
        <button
          className={'navigation ' + (page === 'workflows' ? 'is-active' : '')}
          onClick={() => { setPage('workflows'); setSelected(null); }}
        >
          <Icon name="grid" />Workflows<span className="count">{effectiveWorkflows.length}</span>
        </button>

        <button className="new-workflow" onClick={newWorkflow}>
          <Icon name="plus" />New workflow
        </button>

        <button
          className={'navigation ' + (page === 'settings' ? 'is-active' : '')}
          onClick={openSettings}
        >
          <Icon name="settings" />Settings
        </button>

        <button
          className={'navigation ' + (page === 'community' ? 'is-active' : '')}
          onClick={() => setPage('community')}
        >
          <Icon name="chat" />Community
          <span className="count">{effectiveCommunity.filter(e => e.state === 'AWAITING_APPROVAL').length}</span>
        </button>

        <div className="nav-label workflow-label">
          YOUR WORKFLOWS <span>{active} active</span>
        </div>

        <div className="workflow-nav">
          {effectiveWorkflows.map(c => (
            <button
              className={c.id === selected && page === 'workflows' ? 'selected' : ''}
              key={c.id}
              onClick={() => select(c)}
            >
              <span className={'state-dot ' + (c.state || '').toLowerCase()} />
              <div>
                {c.brief.title}
                <small>{STATUS[c.state] || c.state}</small>
              </div>
              {c.input_requests?.some(q => q.status === 'OPEN') && <span className="tiny-alert">!</span>}
            </button>
          ))}
          {!effectiveWorkflows.length && <p>Your workflows will appear here.</p>}
        </div>

        {!isPilot && (
          <button
            className={'inbox-button ' + (notifications.length ? 'needs-input' : '')}
            onClick={() => setInbox(!inbox)}
          >
            <Icon name="bell" />
            <div>
              Your input
              <small>{notifications.length ? 'Bots are waiting for you' : 'No open requests'}</small>
            </div>
            <b>{effectiveNotifications.length}</b>
          </button>
        )}

        <div className="user-profile-badge">
          <span className="owner-avatar">{(auth.user?.name || auth.user?.email || 'V')[0].toUpperCase()}</span>
          <div className="user-profile-info">
            <b>{auth.user?.name || 'Workspace Owner'}</b>
            <small>{auth.user?.email || 'vitabsquare@gmail.com'}</small>
          </div>
          <button type="button" className="signout-btn" title="Sign out" onClick={handleLogout}>
            <Icon name="logout" size={14} />
          </button>
        </div>

        <div className="sidebar-foot">
          <span className={'online-dot ' + (!connected ? 'offline' : '')} />
          {isPilot ? 'Pilot Sandbox Active' : connected ? 'Workspace connected' : 'Connection lost'}
          <small>
            {isPilot
              ? 'Interactive Demo · In-Browser'
              : (settings.deployment_mode === 'server' ? 'Private server' : 'Local workspace') +
                ' · ' +
                (settings.publishing_mode === 'live' ? 'Live publishing' : 'Simulation')}
          </small>
        </div>
      </aside>

      <main className="main">
        {isPilot && (
          <div className="pilot-live-banner">
            <div className="pilot-live-badge">
              <span className="pilot-pulsing-dot" />
              <span>LIVE PILOT DEMO</span>
            </div>
            <div className="pilot-live-desc">
              Interactive Sandbox · Testing Vtab Square Multi-Agent Marketing Engine
            </div>
            <a href="https://www.vtabsquare.com" target="_blank" rel="noreferrer" className="pilot-live-cta">
              Book Enterprise Access ↗
            </a>
          </div>
        )}

        <header className="topbar">
          <div>
            <span>Marketing Manager</span>
            <Icon name="arrow" size={13} />
            <b>{page === 'settings' ? 'Settings' : page === 'community' ? 'Community inbox' : current ? current.brief.title : 'All workflows'}</b>
          </div>
          <div className="top-actions">
            {!isPilot && (
              <button className="button ghost" onClick={() => setPage('platform')}>
                <Icon name="bolt" size={14} />Control center
              </button>
            )}
            {!isPilot && (
              <button className="button ghost" onClick={openAuditTrail}>
                <Icon name="shield" size={14} />Audit trail
              </button>
            )}
            <span
              className="mode-badge"
              style={isPilot ? { background: '#312e81', color: '#c7d2fe', borderColor: '#6366f1' } : {}}
            >
              {isPilot ? 'PILOT DEMO' : (settings.data_mode || 'standalone').toUpperCase()}
              <span className="status-dot" />
            </span>
            {!isPilot && (
              <button
                className="notification-button"
                aria-label="Open input notifications"
                onClick={() => setInbox(!inbox)}
              >
                <Icon name="bell" />
                {notifications.length > 0 && <b>{effectiveNotifications.length}</b>}
              </button>
            )}
            <span className="owner-avatar" title={auth.user?.email}>
              {(auth.user?.name || auth.user?.email || 'V')[0].toUpperCase()}
            </span>
            <button
              type="button"
              className="button ghost"
              style={{ padding: '6px 11px', fontSize: 11, gap: 6 }}
              title="Sign out"
              onClick={handleLogout}
            >
              <Icon name="logout" size={13} />Sign out
            </button>
          </div>
        </header>

        {!connected && (
          <div className="connection-warning">
            Connection lost. The last saved status is shown. Keep the Python launcher running.
          </div>
        )}
        {error && (
          <div className="notice error" role="alert">
            {error}
            <button aria-label="Dismiss error" onClick={() => setError('')}><Icon name="close" /></button>
          </div>
        )}
        {notice && <div className="notice success" role="status">{notice}</div>}

        {inbox && !isPilot && (
          <section className="inbox-panel">
            <div className="section-heading">
              <div>
                <h2>Your input is needed</h2>
                <p>Each request belongs to its own workflow. Other eligible bot tasks continue.</p>
              </div>
              <button className="icon-button" aria-label="Close notifications" onClick={() => setInbox(false)}>
                <Icon name="close" />
              </button>
            </div>
            {notifications.length ? (
              notifications.map(q => (
                <button
                  key={q.id}
                  onClick={() => {
                    const c = effectiveWorkflows.find(item => item.id === q.campaign_id);
                    if (c) select(c);
                  }}
                  className="notification-item"
                >
                  <Bot role={q.role} size={36} />
                  <div>
                    <b>{q.workflow}</b>
                    <p>{q.question}</p>
                    <small>
                      {BOTS[q.role]?.name} · {q.kind === 'approval' ? 'Content approval' : q.kind === 'attention' ? 'Action needed' : 'Answer requested'}
                    </small>
                  </div>
                  <Icon name="arrow" />
                </button>
              ))
            ) : (
              <div className="quiet">
                <Icon name="check" />
                <p>You are all caught up.</p>
              </div>
            )}
          </section>
        )}

        {page === 'community' ? (
          <CommunityInbox
            community={effectiveCommunity}
            api={api}
            act={act}
            busy={busy}
            setNotice={setNotice}
            setError={setError}
            isPilot={isPilot}
            onPilotUpdate={handlePilotCommunityDecision}
          />
        ) : page === 'settings' && form ? (
          <div className="settings-page">
            <div className="page-heading">
              <div className="kicker">CONFIGURE ONCE. RUN MANY WORKFLOWS.</div>
              <h1>Your manager's workspace</h1>
              <p>Define the model and approved brand facts. Each new workflow keeps its own snapshot.</p>
            </div>
            <form
              onSubmit={e => {
                e.preventDefault();
                if (isPilot) {
                  handleSaveBrandFacts();
                  return;
                }
                act(async () => {
                  const payload = {
                    provider: form.provider,
                    model: form.model,
                    brand: form.brand,
                    social_keys: form.social_keys || {},
                    publishing_mode: form.publishing_mode || 'live',
                    platforms: form.platforms || [],
                    image_provider: form.image_provider || 'template',
                    hf_model: form.hf_model || 'black-forest-labs/FLUX.1-schnell',
                    hf_provider: form.hf_provider || 'auto'
                  };
                  if (form.api_key.trim()) payload.api_key = form.api_key.trim();
                  const s = await api('/settings', 'PUT', payload);
                  setForm({ ...s, api_key: '', brand: { ...s.brand } });
                  setNotice('Settings saved. Test the saved Gemini connection before creating workflows.');
                });
              }}
            >
              <div className="settings-columns">
                <section className={'card settings-card ' + (isPilot ? 'pilot-locked' : '')}>
                  {isPilot && (
                    <div className="pilot-lock-badge">
                      <Icon name="shield" size={12} /> Locked in Pilot Sandbox
                    </div>
                  )}
                  <div className="card-heading">
                    <Bot role="manager" />
                    <div>
                      <h2>Model connection</h2>
                      <p>Your bots share a swappable model gateway.</p>
                    </div>
                  </div>
                  <label>
                    AI provider
                    <select
                      aria-label="AI provider"
                      value={form.provider}
                      onChange={e =>
                        setForm({
                          ...form,
                          provider: e.target.value,
                          model: e.target.value === 'demo' ? 'deterministic-demo-v1' : settings.environment_model || ''
                        })
                      }
                    >
                      <option value="gemini">Google Gemini</option>
                    </select>
                  </label>
                  {form.provider === 'gemini' && (
                    <>
                      <label>
                        Model identifier
                        <input
                          required
                          value={form.model}
                          onChange={e => setForm({ ...form, model: e.target.value })}
                          placeholder="Model available in your AI Studio account"
                        />
                      </label>
                      <label>
                        API key
                        <input
                          type="password"
                          autoComplete="new-password"
                          value={form.api_key}
                          onChange={e => setForm({ ...form, api_key: e.target.value })}
                          placeholder={settings.has_api_key ? 'Saved key — leave blank to keep' : 'Paste your Gemini API key'}
                        />
                      </label>
                      <p className="help">Encrypted in the workspace database. Use inputs permitted for your account.</p>
                    </>
                  )}
                  <div className={'ready-line ' + (!settings.ready ? 'not-ready' : '')}>
                    <span className="status-dot" />
                    {settings.ready ? 'Saved configuration ready' : 'Save and test Gemini to continue'}
                  </div>
                  <button
                    type="button"
                    className="button ghost"
                    disabled={busy || isPilot}
                    onClick={() =>
                      act(async () => {
                        await api('/settings/test', 'POST');
                        setNotice('Connection and structured output test passed.');
                      })
                    }
                  >
                    Test saved connection
                  </button>
                </section>

                <section className="card settings-card">
                  <div className="card-heading">
                    <Icon name="shield" size={28} />
                    <div>
                      <h2>Approved brand facts</h2>
                      <p>These are the facts your bots can use.</p>
                    </div>
                  </div>
                  {[
                    ['name', 'Brand name'],
                    ['product', 'Product or service'],
                    ['price', 'Exact price'],
                    ['tone', 'Brand tone']
                  ].map(([key, label]) => (
                    <label key={key}>
                      {label}
                      <input
                        required
                        maxLength={key === 'price' ? 200 : key === 'product' ? 300 : key === 'name' ? 120 : 200}
                        value={form.brand[key] || ''}
                        onChange={e => setForm({ ...form, brand: { ...form.brand, [key]: e.target.value } })}
                      />
                    </label>
                  ))}
                  <label>
                    Other approved facts
                    <textarea
                      maxLength="4000"
                      rows="3"
                      value={form.brand.facts || ''}
                      onChange={e => setForm({ ...form, brand: { ...form.brand, facts: e.target.value } })}
                    />
                  </label>
                  {isPilot && (
                    <button
                      type="button"
                      className="button primary save-facts-btn"
                      onClick={handleSaveBrandFacts}
                    >
                      <Icon name="check" size={14} /> Save Approved Facts
                    </button>
                  )}
                </section>

                <section className={'card settings-card ' + (isPilot ? 'pilot-locked' : '')}>
                  {isPilot && (
                    <div className="pilot-lock-badge">
                      <Icon name="shield" size={12} /> Locked in Pilot Sandbox
                    </div>
                  )}
                  <div className="card-heading">
                    <Icon name="link" size={28} />
                    <div>
                      <h2>Social integrations</h2>
                      <p>Credentials stay encrypted on the server.</p>
                    </div>
                  </div>
                  <label>
                    Publishing mode
                    <select
                      value={form.publishing_mode || 'live'}
                      onChange={e => setForm({ ...form, publishing_mode: e.target.value })}
                    >
                      <option value="simulation">Simulation</option>
                      <option value="live">Live — posts after your approval</option>
                    </select>
                  </label>
                  <label>
                    Publishing destinations (Select all that apply)
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 6, marginBottom: 10 }}>
                      {[
                        ['instagram', 'Instagram'],
                        ['facebook', 'Facebook Page'],
                        ['whatsapp', 'WhatsApp'],
                        ['discord', 'Discord'],
                        ['linkedin', 'LinkedIn'],
                        ['twitter', 'X / Twitter']
                      ].map(([key, label]) => {
                        const activeKey = (form.platforms || []).includes(key);
                        return (
                          <button
                            type="button"
                            key={key}
                            className={'button ' + (activeKey ? 'primary' : 'ghost')}
                            style={{ padding: '6px 14px', fontSize: 13, borderRadius: 20 }}
                            onClick={() => {
                              const curr = form.platforms || [];
                              const next = activeKey ? curr.filter(p => p !== key) : [...curr, key];
                              setForm({ ...form, platforms: next });
                            }}
                          >
                            {activeKey ? '✓ ' : '+ '}
                            {label}
                          </button>
                        );
                      })}
                    </div>
                  </label>
                  {[
                    ['discord_webhook', 'Discord webhook URL'],
                    ['facebook_page_id', 'Facebook Page ID'],
                    ['facebook_page_token', 'Facebook Page Access Token'],
                    ['facebook_app_secret', 'Facebook App Secret (webhook HMAC)'],
                    ['facebook_verify_token', 'Facebook Webhook Verify Token'],
                    ['instagram_account_id', 'Instagram Business Account ID'],
                    ['instagram_access_token', 'Instagram Access Token (optional if using Page Token)'],
                    ['instagram_verify_token', 'Instagram Webhook Verify Token'],
                    ['whatsapp_phone_number_id', 'WhatsApp Phone Number ID'],
                    ['whatsapp_token', 'WhatsApp Cloud API Access Token'],
                    ['whatsapp_recipient', 'WhatsApp Recipient Phone Number'],
                    ['twitter_access_token', 'X OAuth user access token'],
                    ['twitter_api_key', 'X app API key'],
                    ['twitter_api_secret', 'X app API secret'],
                    ['twitter_client_secret', 'X OAuth 2.0 client secret (webhooks)'],
                    ['linkedin_token', 'LinkedIn access token'],
                    ['linkedin_author', 'LinkedIn author URN']
                  ].map(([key, label]) => (
                    <label key={key}>
                      {label}
                      <input
                        type="password"
                        autoComplete="new-password"
                        value={form.social_keys?.[key] || ''}
                        placeholder={settings.configured_integrations?.[key] ? 'Saved — leave untouched to keep' : 'Enter ' + label}
                        onChange={e => setForm({ ...form, social_keys: { ...form.social_keys, [key]: e.target.value } })}
                      />
                    </label>
                  ))}
                  <p className="help">
                    Multi-platform publishing enabled. When multiple destinations are selected, your campaign publishes to all of them simultaneously with one approval.
                  </p>
                </section>

                <section className={'card settings-card ' + (isPilot ? 'pilot-locked' : '')}>
                  {isPilot && (
                    <div className="pilot-lock-badge">
                      <Icon name="shield" size={12} /> Locked in Pilot Sandbox
                    </div>
                  )}
                  <div className="card-heading">
                    <Bot role="creative" />
                    <div>
                      <h2>Creative studio</h2>
                      <p>Campaign-specific direction. Your choice of image engine.</p>
                    </div>
                  </div>
                  <label>
                    Image provider
                    <select
                      value={form.image_provider || 'template'}
                      onChange={e => setForm({ ...form, image_provider: e.target.value })}
                    >
                      <option value="template">Local vector template (offline)</option>
                      <option value="huggingface">Hugging Face Inference Providers</option>
                      <option value="pollinations">Pollinations</option>
                    </select>
                  </label>
                  <label>
                    Hugging Face token
                    <input
                      type="password"
                      autoComplete="new-password"
                      value={form.social_keys?.hf_token || ''}
                      placeholder={settings.configured_integrations?.hf_token ? 'Saved — leave untouched to keep' : 'Paste your inference token'}
                      onChange={e => setForm({ ...form, social_keys: { ...form.social_keys, hf_token: e.target.value } })}
                    />
                  </label>
                  <label>
                    Image model
                    <input
                      value={form.hf_model || 'black-forest-labs/FLUX.1-schnell'}
                      onChange={e => setForm({ ...form, hf_model: e.target.value })}
                    />
                  </label>
                  <label>
                    Inference provider
                    <input
                      value={form.hf_provider || 'auto'}
                      onChange={e => setForm({ ...form, hf_provider: e.target.value })}
                    />
                  </label>
                </section>
              </div>

              {!isPilot && (
                <div className="form-actions">
                  <button className="button primary" disabled={busy}>
                    Save settings<Icon name="check" />
                  </button>
                </div>
              )}
            </form>
          </div>
        ) : current ? (
          <>
            <div className="workflow-heading">
              <div>
                <div className="kicker">INDEPENDENT WORKFLOW <span className="divider">/</span> {current.id.slice(0, 8)}</div>
                <h1>{current.brief.title}</h1>
                <p>{current.brief.goal}</p>
              </div>
              <div>
                <span className={'pill ' + (current.state || '').toLowerCase()}>{STATUS[current.state] || current.state}</span>
                {current.nodes?.analytics?.state === 'SCHEDULED_WAIT' && (
                  <button
                    className="button primary"
                    style={{ marginLeft: 8, marginRight: 8 }}
                    disabled={busy}
                    onClick={() => {
                      if (isPilot) {
                        setNotice('Analytics Bot triggered! Collecting platform metrics...');
                        setTimeout(() => setNotice('Simulated 24h platform metrics updated.'), 1500);
                        return;
                      }
                      act(async () => {
                        await api('/campaigns/' + current.id + '/collect-metrics', 'POST');
                        setNotice('Analytics Bot triggered! Collecting platform metrics...');
                      });
                    }}
                  >
                    Collect Analytics Now
                  </button>
                )}
                <a className="button ghost export" href={'/api/campaigns/' + current.id + '/export'} download>
                  <Icon name="file" />Export
                </a>
              </div>
            </div>

            <div className="workflow-layout">
              <aside className="team-panel">
                <div className="team-heading">
                  <span>YOUR BOT TEAM</span>
                  <b>{Object.values(current.nodes || {}).filter(n => n.state === 'ACCEPTED').length}/10 done</b>
                </div>
                {ROLES.map(role => {
                  const node = (current.nodes && current.nodes[role]) || { state: 'PENDING' };
                  return (
                    <button
                      key={role}
                      className={'team-member ' + (focusedBot === role ? 'focused' : '')}
                      onClick={() => {
                        setFocusedBot(focusedBot === role ? null : role);
                        setTab('conversation');
                      }}
                    >
                      <Bot role={role} size={39} state={node.state} />
                      <div>
                        <b>{BOTS[role].name}</b>
                        <small className={'node-state ' + (node.state || '').toLowerCase()}>
                          {role === 'manager' && !['COMPLETED', 'CANCELLED'].includes(current.state)
                            ? current.state === 'AWAITING_APPROVAL'
                              ? 'Waiting for your review'
                              : 'Coordinating the team'
                            : STATUS[node.state] || node.state}
                        </small>
                      </div>
                      {node.state === 'ACCEPTED' ? (
                        <Icon name="check" size={14} />
                      ) : node.state === 'RUNNING' ? (
                        <span className="working-dot" />
                      ) : ['WAITING_INPUT', 'BLOCKED'].includes(node.state) ? (
                        <span className="tiny-alert">!</span>
                      ) : null}
                    </button>
                  );
                })}
                <div className="team-note">
                  <Icon name="link" size={15} />
                  <p>Independent bot tasks. The manager coordinates required handoffs.</p>
                </div>
              </aside>

              <section className="conversation-panel">
                <div className="panel-tabs">
                  <button
                    className={tab === 'conversation' ? 'active' : ''}
                    onClick={() => setTab('conversation')}
                  >
                    <Icon name="chat" />Team conversation
                  </button>
                  <button
                    className={tab === 'map' ? 'active' : ''}
                    onClick={() => setTab('map')}
                  >
                    <Icon name="grid" />Workflow map
                  </button>
                  <span className="live-indicator">
                    <span className="status-dot" />
                    {connected ? 'Live' : 'Offline'}
                  </span>
                </div>

                {tab === 'conversation' ? (
                  <>
                    <div className="chat-context">
                      <Bot role="manager" size={30} />
                      <div>
                        <b>{focusedBot ? BOTS[focusedBot].name + ' · conversation filter' : 'Marketing Manager is coordinating this workflow'}</b>
                        <small>
                          {focusedBot
                            ? 'Messages to and from this bot'
                            : current.snapshot?.publishing === 'live'
                            ? 'Live destination: ' + (current.snapshot.platforms || []).join(', ')
                            : 'Simulation · Saved automatically'}
                        </small>
                      </div>
                      {focusedBot && (
                        <button className="icon-button" aria-label="Clear bot filter" onClick={() => setFocusedBot(null)}>
                          <Icon name="close" size={15} />
                        </button>
                      )}
                    </div>

                    <div
                      className="message-feed"
                      ref={feedBox}
                      onScroll={() => {
                        const box = feedBox.current;
                        if (box) follow.current = box.scrollHeight - box.scrollTop - box.clientHeight < 70;
                      }}
                    >
                      {shownEvents.map((event, idx) => (
                        <Message key={event.id || idx} event={event} />
                      ))}
                      {running.length > 0 && (
                        <div className="typing-row">
                          {running.map(role => (
                            <span key={role}>
                              <Bot role={role} size={25} />
                              {BOTS[role]?.name || role} is working
                              <span className="typing-dots">•••</span>
                            </span>
                          ))}
                        </div>
                      )}
                      {isPilot && current?.state === 'AWAITING_APPROVAL' && (
                        <div className="pilot-approval-banner" style={{
                          margin: '14px 10px',
                          background: 'linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%)',
                          border: '2px solid #818cf8',
                          borderRadius: 12,
                          padding: '16px 18px',
                          boxShadow: '0 8px 30px rgba(99, 102, 241, 0.45)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          gap: 16
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            <Bot role="manager" size={40} />
                            <div>
                              <div style={{ fontSize: 10, fontWeight: 800, color: '#a5b4fc', letterSpacing: '1px', textTransform: 'uppercase' }}>
                                ⚡ Action Required
                              </div>
                              <div style={{ fontSize: 14, fontWeight: 800, color: '#ffffff', margin: '2px 0' }}>
                                Content & Creative Ready for Approval
                              </div>
                              <div style={{ fontSize: 12, color: '#cbd5e1' }}>
                                Marketing Manager verified 100% Brand Guardian fidelity. Approve to broadcast!
                              </div>
                            </div>
                          </div>
                          <button
                            type="button"
                            className="button primary"
                            style={{
                              background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                              color: '#ffffff',
                              fontWeight: 700,
                              padding: '10px 20px',
                              fontSize: 13,
                              borderRadius: 8,
                              border: 'none',
                              cursor: 'pointer',
                              boxShadow: '0 4px 14px rgba(99, 102, 241, 0.5)',
                              flexShrink: 0
                            }}
                            onClick={() => handlePilotApprove(current.id)}
                          >
                            Approve & Broadcast →
                          </button>
                        </div>
                      )}
                      <div ref={feedEnd} />
                    </div>

                    <div className="chat-footer">
                      <Icon name="shield" size={15} />
                      <span>Messages reflect saved assignments, results and handoffs. Replies go to open input requests.</span>
                    </div>
                  </>
                ) : (
                  <div className="map-panel">
                    <div className="map-title">
                      <h2>One manager. Independent bot workflows.</h2>
                      <p>Branches run in parallel once their required inputs are ready.</p>
                    </div>
                    <div className="map-flow">
                      <MapNode role="research" current={current} />
                      <div className="flow-connector">↓</div>
                      <MapNode role="strategy" current={current} />
                      <div className="flow-connector">↓</div>
                      <div className="parallel-group">
                        <MapNode role="writing" current={current} />
                        <MapNode role="creative" current={current} />
                      </div>
                      <div className="parallel-caption">Independent tasks · run in parallel</div>
                      <div className="flow-connector">↓</div>
                      <MapNode role="brand_review" current={current} />
                      <div className="flow-connector">↓</div>
                      <MapNode role="manager" current={current} />
                      <div className="approval-gate">
                        <Icon name="person" size={14} /> Your exact-version approval
                      </div>
                      <MapNode role="publishing" current={current} />
                      <div className="flow-connector">↓</div>
                      <div className="parallel-group">
                        <div>
                          <MapNode role="analytics" current={current} />
                          <div className="flow-connector">↓</div>
                          <MapNode role="optimization" current={current} />
                        </div>
                        <MapNode role="engagement" current={current} />
                      </div>
                    </div>
                  </div>
                )}
              </section>

              <aside className="work-inspector">
                <div className="inspector-title">
                  <Icon name="bell" />HUMAN INPUT & RESULTS
                </div>

                {openRequests.length > 0 ? (
                  openRequests.map(q => (
                    <section key={q.id} className="request-card">
                      <div className="request-top">
                        <Bot role={q.role} size={34} />
                        <div>
                          <b>{BOTS[q.role]?.name}</b>
                          <small>YOUR INPUT IS NEEDED</small>
                        </div>
                      </div>
                      <h3>{q.question}</h3>
                      <p>{q.reason}</p>
                      {q.kind === 'approval' ? (
                        <>
                          <button
                            className="button primary full"
                            disabled={busy}
                            onClick={() => {
                              if (isPilot) {
                                handlePilotApprove(current.id);
                                return;
                              }
                              act(() =>
                                api('/campaigns/' + current.id + '/approve', 'POST', {
                                  content_hash: current.content_hash,
                                  note: 'Approved in the workflow panel.'
                                })
                              );
                            }}
                          >
                            Approve {current.snapshot?.publishing === 'live' ? 'live publication' : 'simulation'}
                            <Icon name="check" />
                          </button>
                          <textarea
                            aria-label="Revision instructions"
                            rows="2"
                            value={revision}
                            onChange={e => setRevision(e.target.value)}
                            placeholder="Or describe the changes needed"
                          />
                          <button
                            className="button ghost full"
                            disabled={busy || !revision.trim()}
                            onClick={() => {
                              if (isPilot) {
                                setNotice('Revision requested in simulation.');
                                setRevision('');
                                return;
                              }
                              act(async () => {
                                await api('/campaigns/' + current.id + '/revise', 'POST', {
                                  content_hash: current.content_hash,
                                  note: revision
                                });
                                setRevision('');
                              });
                            }}
                          >
                            Request changes
                          </button>
                        </>
                      ) : (
                        <form
                          onSubmit={e => {
                            e.preventDefault();
                            if (isPilot) {
                              setNotice('Answer sent to bot.');
                              setAnswers(a => ({ ...a, [q.id]: '' }));
                              return;
                            }
                            act(async () => {
                              await api('/campaigns/' + current.id + '/input', 'POST', {
                                request_id: q.id,
                                answer: answers[q.id]
                              });
                              setAnswers(a => ({ ...a, [q.id]: '' }));
                            });
                          }}
                        >
                          <textarea
                            aria-label={'Reply to ' + BOTS[q.role]?.name}
                            required
                            maxLength="2000"
                            rows="3"
                            value={answers[q.id] || ''}
                            onChange={e => setAnswers({ ...answers, [q.id]: e.target.value })}
                            placeholder="Type your answer…"
                          />
                          <button className="button primary full" disabled={busy || !answers[q.id]?.trim()}>
                            Send & resume bot<Icon name="send" />
                          </button>
                        </form>
                      )}
                    </section>
                  ))
                ) : (
                  <div className="no-input">
                    <Icon name="check" />
                    <div>
                      <b>No input needed right now</b>
                      <p>Your bots will notify you here when they need a decision.</p>
                    </div>
                  </div>
                )}

                {blocked.map(([role, node]) => (
                  <section key={role} className="blocked-card">
                    <Bot role={role} size={32} />
                    <h3>{BOTS[role]?.name} needs attention</h3>
                    <p>{node.error?.message}</p>
                    <button
                      className="button ghost full"
                      disabled={busy}
                      onClick={() => act(() => api('/campaigns/' + current.id + '/retry', 'POST'))}
                    >
                      Retry after fixing
                    </button>
                  </section>
                ))}

                <section className="result-card">
                  <div className="result-heading">
                    <Icon name="file" />
                    <h2>Content preview</h2>
                    {current.results?.writing && <span>v{(current.revisions || 0) + 1}</span>}
                  </div>
                  {current.results?.writing ? (
                    <>
                      <h3>{current.results.writing.output?.headline}</h3>
                      <p className="caption">{current.results.writing.output?.caption}</p>
                      {current.results?.creative && (
                        <>
                          {current.id.startsWith('pilot_') ? (
                            <div
                              className="pilot-svg-preview"
                              style={{ borderRadius: 10, overflow: 'hidden', margin: '12px 0', border: '1px solid #312e81', background: '#0b0f19' }}
                              dangerouslySetInnerHTML={{
                                __html: renderPilotSvg(
                                  current.results.writing?.output?.headline || current.brief?.title,
                                  current.snapshot?.brand?.name || 'Vtab Square',
                                  current.results.writing?.output?.price_claim || current.snapshot?.brand?.price || 'Free to join',
                                  current.results.creative?.output?.primary_hex || '#1e1b4b',
                                  current.results.creative?.output?.accent_hex || '#6366f1',
                                  current.brief?.audience || '',
                                  current.brief?.destinations || current.snapshot?.platforms || ['instagram', 'facebook', 'whatsapp', 'linkedin']
                                )
                              }}
                            />
                          ) : (
                            <img
                              src={'/api/campaigns/' + current.id + '/creative.svg?v=' + (current.content_hash || current.nodes?.creative?.generation || '1')}
                              alt="Campaign creative preview"
                            />
                          )}
                          <p className="creative-direction">{current.results.creative.output?.art_direction}</p>
                          {current.results.writing?.output?.variants?.length > 0 && (
                            <div className="pilot-variants-box" style={{ marginTop: 14, borderTop: '1px solid #e0e7ff', paddingTop: 12 }}>
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                                <h4 style={{ fontSize: 13, textTransform: 'uppercase', color: '#4f46e5', letterSpacing: '0.05em', margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
                                  <Icon name="link" size={14} /> Multi-Channel Copy Adaptations
                                </h4>
                                <span style={{ fontSize: 11, background: '#e0e7ff', color: '#3730a3', padding: '2px 8px', borderRadius: 99, fontWeight: 700 }}>
                                  {current.results.writing.output.variants.length} Channels
                                </span>
                              </div>
                              <div style={{ display: 'grid', gap: 10 }}>
                                {current.results.writing.output.variants.map((v, i) => (
                                  <div key={i} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: '10px 12px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                                      <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: '#4f46e5', background: '#eef2ff', padding: '2px 8px', borderRadius: 4 }}>
                                        {v.destination}
                                      </span>
                                      <span style={{ fontSize: 11, color: '#16a34a', fontWeight: 600 }}>✓ Verified Live Simulation</span>
                                    </div>
                                    <div style={{ fontWeight: 600, fontSize: 13, color: '#1e293b', marginBottom: 4 }}>{v.headline}</div>
                                    <div style={{ fontSize: 12, color: '#475569', whiteSpace: 'pre-line', lineHeight: 1.45 }}>{v.body}</div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </>
                      )}
                    </>
                  ) : (
                    <div className="result-placeholder">
                      <Bot role="writing" size={48} />
                      <p>The content will appear here when Writer Bot finishes.</p>
                    </div>
                  )}
                </section>

                {current.results?.publishing && (
                  <section className="result-card receipt">
                    <Icon name="check" />
                    <h3>{current.results.publishing.output?.mode === 'live' ? 'Publication confirmed' : 'Simulation confirmed'}</h3>
                    <p>{current.results.publishing.output?.message || 'Campaign published successfully.'}</p>
                    {isPilot && (
                      <button
                        type="button"
                        className="button primary full"
                        style={{ marginTop: 12, background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)' }}
                        onClick={() => setPilotDemoEnd(current)}
                      >
                        🚀 View Demo Summary & Contact For More
                      </button>
                    )}
                  </section>
                )}

                {current.nodes?.analytics?.state === 'SCHEDULED_WAIT' && (
                  <section className="result-card" style={{ borderColor: '#6366f1' }}>
                    <div className="result-heading">
                      <Icon name="chart" />
                      <h2>Analytics Scheduled</h2>
                      <span>24h Window</span>
                    </div>
                    <p className="help">Analytics Bot is scheduled to collect platform metrics after 24 hours. You can also trigger it now on demand.</p>
                    <button
                      className="button primary full"
                      style={{ marginTop: 8 }}
                      disabled={busy}
                      onClick={() => {
                        if (isPilot) {
                          setNotice('Analytics Bot triggered! Collecting platform metrics...');
                          return;
                        }
                        act(async () => {
                          await api('/campaigns/' + current.id + '/collect-metrics', 'POST');
                          setNotice('Analytics Bot triggered! Collecting platform metrics...');
                        });
                      }}
                    >
                      Collect & Analyze Metrics Now
                    </button>
                  </section>
                )}

                {current.results?.analytics && (() => {
                  const m = current.results.analytics.metrics || {};
                  const eng = m.engagements ?? m.records?.find(r => r.available)?.engagements ?? 0;
                  return (
                    <section className="result-card">
                      <div className="result-heading">
                        <Icon name="chart" />
                        <h2>Performance</h2>
                        <span>{m.mode === 'live' ? 'Live Measured' : 'Sample'}</span>
                      </div>
                      <div className="metrics">
                        <div>
                          <b>{m.impressions != null ? m.impressions.toLocaleString() : 'Pending (24h)'}</b>
                          <small>Impressions</small>
                        </div>
                        <div>
                          <b>{eng != null ? eng : 0}</b>
                          <small>Interactions (Likes/Comments)</small>
                        </div>
                        <div>
                          <b>{m.engagement_rate_pct != null ? m.engagement_rate_pct + '%' : '—'}</b>
                          <small>Engagement Rate</small>
                        </div>
                      </div>
                      <p className="help">
                        {m.mode === 'live'
                          ? 'Live metrics from Meta Graph API. Organic impressions update over 24h as audiences engage.'
                          : 'Synthetic fixture values, not live campaign results.'}
                      </p>
                      {m.mode === 'live' && (
                        <button
                          type="button"
                          className="button ghost full"
                          style={{ marginTop: 8 }}
                          disabled={busy}
                          onClick={() =>
                            act(async () => {
                              await api('/campaigns/' + current.id + '/collect-metrics', 'POST');
                              setNotice('Refreshed live Instagram metrics from Meta Graph API!');
                            })
                          }
                        >
                          <Icon name="bolt" size={13} />Refresh live metrics
                        </button>
                      )}
                    </section>
                  );
                })()}

                {['research', 'strategy', 'brand_review', 'manager', 'optimization', 'engagement']
                  .filter(r => current.results && current.results[r])
                  .map(role => (
                    <details className="output-detail" key={role}>
                      <summary>
                        <Bot role={role} size={26} />
                        {BOTS[role]?.name} result
                      </summary>
                      <Structured value={current.results[role].output || {}} />
                    </details>
                  ))}

                {!['COMPLETED', 'CANCELLED'].includes(current.state) && (
                  <button
                    className="cancel-workflow"
                    disabled={busy}
                    onClick={() => {
                      if (isPilot) {
                        const list = getPilotWorkflows();
                        const wf = list.find(w => w.id === current.id);
                        if (wf) {
                          wf.state = 'CANCELLED';
                          savePilotWorkflows(list);
                          setWorkflows([...list]);
                        }
                        return;
                      }
                      act(() => api('/campaigns/' + current.id + '/cancel', 'POST'));
                    }}
                  >
                    Stop this workflow
                  </button>
                )}
              </aside>
            </div>
          </>
        ) : (
          <div className="overview">
            <div className="page-heading overview-heading">
              <div>
                <div className="kicker">YOUR AUTOMATION CONTROL ROOM</div>
                <h1>Great campaigns.<br /><span>Built together.</span></h1>
                <p>Your AI team turns a brief into strategy, content and creative. Stay in the conversation. Make the decisions that matter.</p>
              </div>
              <div className="manager-hero">
                <Bot role="manager" size={90} />
                <span>YOUR MAIN AGENT</span>
                <b>Marketing Manager</b>
                <small>Planning · Coordinating · Checking</small>
              </div>
            </div>

            <div className="summary-stats">
              <div>
                <span className="metric-icon"><Icon name="play" /></span>
                <b>{active}</b>
                <p>Active workflows<small>Run independently</small></p>
              </div>

              {!isPilot && (
                <div>
                  <span className="metric-icon orange"><Icon name="bell" /></span>
                  <b>{effectiveNotifications.length}</b>
                  <p>Waiting for you<small>Answer to resume a bot</small></p>
                </div>
              )}

              {isPilot && (
                <div>
                  <span className="metric-icon" style={{ background: '#312e81', borderColor: '#6366f1', color: '#a5b4fc' }}>
                    <Icon name="shield" />
                  </span>
                  <b>Verified</b>
                  <p>Brand Guardian<small>100% Price Fidelity</small></p>
                </div>
              )}

              <div>
                <span className="metric-icon"><Icon name="check" /></span>
                <b>{completed}</b>
                <p>Completed<small>Saved with their results</small></p>
              </div>
            </div>

            {!settings.ready && !isPilot && (
              <div className="setup-needed">
                <Icon name="settings" />
                <div>
                  <b>Configure and test Gemini first.</b>
                  <p>The manager needs a working model connection to start workflows.</p>
                </div>
                <button className="button ghost" onClick={openSettings}>Open Settings</button>
              </div>
            )}

            <div className="section-heading">
              <div>
                <h2>Your workflows</h2>
                <p>Each workflow has its own team conversation, results and input requests.</p>
              </div>
              <button className="button primary" onClick={newWorkflow}>
                <Icon name="plus" />New workflow
              </button>
            </div>

            {effectiveWorkflows.length ? (
              <div className="workflow-cards">
                {effectiveWorkflows.map(c => (
                  <button className="workflow-card" key={c.id} onClick={() => select(c)}>
                    <div className="workflow-card-top">
                      <span className={'pill ' + (c.state || '').toLowerCase()}>{STATUS[c.state] || c.state}</span>
                      <Icon name="arrow" />
                    </div>
                    <h3>{c.brief.title}</h3>
                    <p>{c.brief.goal}</p>
                    <div className="mini-team">
                      {['manager', 'writing', 'creative', 'brand_review'].map(role => (
                        <Bot
                          key={role}
                          role={role}
                          size={32}
                          state={c.nodes && c.nodes[role] ? c.nodes[role].state : 'PENDING'}
                        />
                      ))}
                      <small>
                        {Object.values(c.nodes || {}).filter(n => n.state === 'ACCEPTED').length}/10 done
                      </small>
                    </div>
                    {c.input_requests?.some(q => q.status === 'OPEN') && (
                      <div className="card-input-needed">
                        <Icon name="bell" size={14} />Your input is needed
                      </div>
                    )}
                  </button>
                ))}
              </div>
            ) : (
              <div className="empty-workspace">
                <div className="bot-line">
                  {['research', 'writing', 'manager', 'creative', 'analytics'].map((role) => (
                    <Bot key={role} role={role} size={role === 'manager' ? 68 : 47} />
                  ))}
                </div>
                <h2>Your bots are ready for their first workflow.</h2>
                <p>Create a campaign brief. Your manager assigns the work and coordinates the team.</p>
                <button className="button primary" onClick={newWorkflow}>
                  Create a workflow<Icon name="arrow" />
                </button>
              </div>
            )}

            <div className="scope-note">
              <span className="status-dot" />
              {isPilot
                ? 'Interactive Pilot Sandbox · In-Browser Simulation · Zero API Cost'
                : 'Human approvals · Independent agent workflows · Private workspace'}
            </div>
          </div>
        )}
      </main>

      {attention && !isPilot && (
        <div className="input-toast" role="status">
          <Bot role={attention.role} size={38} />
          <div>
            <small>YOUR INPUT IS NEEDED</small>
            <b>{BOTS[attention.role]?.name} is waiting</b>
            <p>{attention.workflow}</p>
            <button
              onClick={() => {
                shownAttentionId.current = null;
                const c = effectiveWorkflows.find(item => item.id === attention.campaign_id);
                if (c) select(c);
                setAttention(null);
              }}
            >
              Open request <Icon name="arrow" size={12} />
            </button>
          </div>
          <button
            className="icon-button"
            aria-label="Dismiss input notification"
            onClick={() => {
              shownAttentionId.current = null;
              setAttention(null);
            }}
          >
            <Icon name="close" size={14} />
          </button>
        </div>
      )}

      {createOpen && (
        <div className="modal-overlay">
          <section className="create-modal" role="dialog" aria-modal="true" aria-labelledby="create-title">
            <div className="modal-header">
              <div>
                <div className="kicker">NEW INDEPENDENT WORKFLOW</div>
                <h2 id="create-title">Give your bots a brief.</h2>
              </div>
              <button className="icon-button" aria-label="Close new workflow" onClick={() => setCreateOpen(false)}>
                <Icon name="close" />
              </button>
            </div>
            <div className="modal-manager">
              <Bot role="manager" size={43} />
              <p>I'll assign the bot tasks, coordinate their handoffs, and notify you when your input is needed.</p>
            </div>
            {error && <div className="notice error" role="alert">{error}</div>}
            <form
              onSubmit={e => {
                e.preventDefault();
                if (isPilot) {
                  setCreateOpen(false);
                  setError('');
                  const targetBrief = {
                    ...brief,
                    destinations: form?.platforms?.length ? form.platforms : ['instagram', 'facebook', 'whatsapp']
                  };
                  const newWf = simulatePilotCampaign(targetBrief, form?.brand || getPilotBrand(), (updated) => {
                    const refreshed = getPilotWorkflows();
                    setWorkflows([...refreshed]);
                    // COMPLETED is only reached after user clicks Approve (via completePilotCampaign)
                    // AWAITING_APPROVAL pause triggers a refresh so the approval card shows in the inspector
                  });
                  setWorkflows(getPilotWorkflows());
                  select(newWf);
                  return;
                }
                act(async () => {
                  const c = await api('/campaigns', 'POST', brief);
                  setCreateOpen(false);
                  setWorkflows(cs => [c, ...cs]);
                  select(c);
                });
              }}
            >
              <label>
                Workflow name
                <input
                  autoFocus
                  required
                  maxLength="120"
                  value={brief.title}
                  onChange={e => setBrief({ ...brief, title: e.target.value })}
                  placeholder="e.g. Launch our summer package"
                />
              </label>
              <label>
                Target audience
                <input
                  required
                  maxLength="500"
                  value={brief.audience}
                  onChange={e => setBrief({ ...brief, audience: e.target.value })}
                  placeholder="Who should this campaign reach?"
                />
              </label>
              <label>
                Campaign goal
                <textarea
                  required
                  rows="2"
                  maxLength="500"
                  value={brief.goal}
                  onChange={e => setBrief({ ...brief, goal: e.target.value })}
                  placeholder="What should the team achieve?"
                />
              </label>
              <label>
                Campaign direction <span className="optional">optional</span>
                <textarea
                  rows="2"
                  maxLength="2000"
                  value={brief.instructions}
                  onChange={e => setBrief({ ...brief, instructions: e.target.value })}
                  placeholder="Message, constraints or other useful context"
                />
              </label>
              <label>
                Human input checkpoint
                <select
                  aria-label="Human input checkpoint"
                  value={brief.checkpoint}
                  onChange={e => setBrief({ ...brief, checkpoint: e.target.value })}
                >
                  <option value="creative">Creative Bot asks me for visual direction</option>
                  <option value="strategy">Strategy Bot asks me to choose the campaign angle</option>
                  <option value="none">Continue automatically until content approval</option>
                </select>
              </label>
              <p className="help">A waiting bot pauses its own branch. Independent work and other workflows continue.</p>
              {isPilot && (
                <div className="pilot-autofill-banner">
                  <div className="pilot-autofill-banner-left">
                    <span className="pilot-autofill-tag">⚡ DEMO AUTO-FILLED</span>
                    <span className="pilot-autofill-text">
                      Showcase brief ready! Click <strong>Start workflow</strong> below to launch.
                    </span>
                  </div>
                </div>
              )}
              <div className="modal-footer">
                <div>
                  <span className="status-dot" />
                  {isPilot
                    ? 'Pilot Mode · Simulation Only'
                    : (settings.provider === 'demo' ? 'Offline demo' : 'Gemini') +
                      ' · ' +
                      (settings.publishing_mode === 'live' ? 'Live: ' + (settings.platforms || []).join(', ') : 'Simulation')}
                </div>
                <button
                  className={`button primary ${isPilot ? 'pilot-start-btn' : ''}`}
                  disabled={busy || (!isPilot && !settings.ready)}
                >
                  {isPilot ? (
                    <>
                      <span className="pilot-start-indicator">⚡</span>
                      <span>Start workflow</span>
                      <Icon name="arrow" />
                    </>
                  ) : (
                    <>
                      Start workflow<Icon name="arrow" />
                    </>
                  )}
                </button>
              </div>
              {!settings.ready && !isPilot && (
                <p className="form-error">Close this form and configure Gemini in Settings first.</p>
              )}
            </form>
          </section>
        </div>
      )}

      {auditOpen && !isPilot && (
        <div className="modal-overlay" onClick={() => setAuditOpen(false)}>
          <section
            className="create-modal"
            style={{ maxWidth: 860, width: '92%' }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="audit-title"
            onClick={e => e.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <div className="kicker">SYSTEM INTEGRITY & SECURITY</div>
                <h2 id="audit-title">Security & Audit Trail</h2>
              </div>
              <button className="icon-button" aria-label="Close audit trail" onClick={() => setAuditOpen(false)}>
                <Icon name="close" />
              </button>
            </div>
            <p style={{ fontSize: 13, color: '#685b82', margin: '6px 0 14px' }}>
              Immutable record of user actions, approvals, automated bot actions, and platform publications.
            </p>
            {auditLoading ? (
              <div style={{ padding: '40px 0', textAlign: 'center', color: '#7d7099' }}>Loading audit logs…</div>
            ) : auditEvents.length === 0 ? (
              <div style={{ padding: '40px 0', textAlign: 'center', color: '#7d7099' }}>No audit records found.</div>
            ) : (
              <div className="audit-table-wrap">
                <table className="audit-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Actor</th>
                      <th>Role</th>
                      <th>Method</th>
                      <th>Resource Path</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditEvents.map(evt => (
                      <tr key={evt.id}>
                        <td>{evt.at ? new Date(evt.at * 1000).toLocaleString() : '—'}</td>
                        <td><b>{evt.actor || 'anonymous'}</b></td>
                        <td><span style={{ fontSize: 11, color: '#7a6b98' }}>{evt.role || '—'}</span></td>
                        <td><code>{evt.method}</code></td>
                        <td style={{ fontFamily: 'monospace', fontSize: 12, color: '#4f3d73' }}>{evt.path}</td>
                        <td><span className={'status-badge ' + (evt.status < 400 ? 'ok' : 'err')}>{evt.status}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div className="modal-footer" style={{ justifyContent: 'flex-end' }}>
              <button className="button ghost" onClick={() => setAuditOpen(false)}>Close</button>
            </div>
          </section>
        </div>
      )}

      {pilotDemoEnd && (
        <PilotDemoEndModal
          campaign={pilotDemoEnd}
          onClose={() => setPilotDemoEnd(null)}
          onView={(c) => select(c)}
        />
      )}
    </div>
  );
}

function Message({ event }) {
  const bot = BOTS[event.actor] || BOTS.manager;
  return (
    <article className={'message ' + (event.kind || '') + (event.actor === 'local-owner' ? ' human-message' : '')}>
      <Bot role={event.actor} size={34} />
      <div className="message-body">
        <div className="message-meta">
          <b>{bot?.name || event.actor}</b>
          {event.target && (
            <>
              <span>→</span>
              <strong>{BOTS[event.target]?.name || event.target}</strong>
            </>
          )}
          <time>{new Date((event.at || Date.now() / 1000) * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time>
        </div>
        <div className="message-text">{event.message}</div>
        {event.kind === 'input_needed' && (
          <span className="message-label">
            <Icon name="bell" size={12} />Your input is needed · Answer in the panel
          </span>
        )}
        {event.kind === 'handoff' && (
          <span className="message-label">
            <Icon name="link" size={12} />Checked result handed off
          </span>
        )}
      </div>
    </article>
  );
}

function MapNode({ role, current }) {
  const n = (current.nodes && current.nodes[role]) || { state: 'PENDING' };
  return (
    <div className={'map-node ' + (n.state || '').toLowerCase()}>
      <Bot role={role} size={31} state={n.state} />
      <div>
        <b>{BOTS[role]?.name || role}</b>
        <small>{STATUS[n.state] || n.state}</small>
      </div>
      {n.state === 'ACCEPTED' && <Icon name="check" size={15} />}
    </div>
  );
}

function Structured({ value }) {
  return (
    <div className="structured">
      {Object.entries(value || {})
        .filter(([k, v]) => k !== 'input_request' && v !== null)
        .map(([k, v]) => (
          <div key={k}>
            <b>{k.replaceAll('_', ' ')}</b>
            {Array.isArray(v) ? (
              <ul>
                {v.map((item, i) => (
                  <li key={i}>{typeof item === 'object' ? item.text + ' · ' + (item.source_ref || '') : item}</li>
                ))}
              </ul>
            ) : (
              <p>{typeof v === 'boolean' ? (v ? 'Yes' : 'No') : v}</p>
            )}
          </div>
        ))}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
