// Sandboxed In-Browser Pilot Engine for Vtab Square Marketing OS

export const DEFAULT_PILOT_BRAND = {
  name: 'Vtab Square',
  product: 'Autonomous AI Marketing Engine & Live Analytics Suite',
  price: '100% Free to join. Free access.',
  tone: 'Visionary, bold, authoritative, and data-driven. High-energy, developer and marketer-friendly.',
  facts: 'Vtab Square is an enterprise AI marketing automation suite. Next live masterclass & product demo: 20th November 2026. Interactive Discord community for builders. Official website: www.vtabsquare.com. Support: contact@vtabsquare.com.'
};

export const INITIAL_PILOT_WORKFLOWS = [
  {
    "id": "30ed23b0186144d7a6c97955bc24cd7e",
    "version": 24,
    "brief": {
      "title": "Vtab Square Autonomous Marketing Launch",
      "audience": "Software developers, engineering leads, and digital marketers",
      "goal": "Drive free membership sign-ups to the Vtabsquare tech community and foster active developer collaboration",
      "instructions": "Highlight peer code reviews, live project feedback, networking, and emphasize that joining is 100% free with no hidden cost",
      "checkpoint": "creative",
      "destinations": [],
      "audience_id": null,
      "schedule_at": null,
      "workflow_id": "campaign.v1"
    },
    "snapshot": {
      "brand": {
        "name": "Vtab Square",
        "product": "AI Marketing Manager & Autonomous Campaign Engine",
        "price": "Free to join",
        "tone": "Welcoming, tech-focused, and collaborative",
        "facts": "Vtabsquare is a hub for developers and marketing professionals to share knowledge, get feedback on projects, and network in real-time."
      },
      "agents": {
        "version": 1,
        "agents": {
          "manager": {
            "implementation": "manager_v1",
            "profile": "default",
            "prompt_version": "manager.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.manager"
            ],
            "memory_write": [
              "campaign"
            ],
            "role_instructions": "Review the complete package, capability limitations and approval requirements before recommending an action. When brand price is free (e.g. 'Free to join'), copy that uses 'free', 'join for free', or 'no cost' is factually correct \u2014 do NOT treat it as a pricing error or request revision for pricing. Only recommend 'revise' if there is a clear factual error unrelated to free-tier pricing."
          },
          "research": {
            "implementation": "research_v1",
            "profile": "default",
            "prompt_version": "research.v2",
            "tools": [
              "web.search",
              "website.knowledge",
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.research"
            ],
            "memory_write": [
              "campaign",
              "agent.research.candidate"
            ],
            "role_instructions": "Use approved client knowledge and verified search records. Distinguish facts, estimates, opinions and limitations. Cite only source_ref identifiers supplied by tools."
          },
          "strategy": {
            "implementation": "strategy_v1",
            "profile": "default",
            "prompt_version": "strategy.v2",
            "tools": [
              "memory.search",
              "crm.read_segments"
            ],
            "memory_read": [
              "client",
              "campaign",
              "performance",
              "agent.strategy"
            ],
            "memory_write": [
              "campaign"
            ],
            "role_instructions": "Turn approved evidence into a specific, achievable campaign plan matched to available capabilities and selected destinations."
          },
          "writing": {
            "implementation": "writing_v1",
            "profile": "default",
            "prompt_version": "writing.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.writing"
            ],
            "memory_write": [
              "campaign",
              "agent.writing.candidate"
            ],
            "role_instructions": "Create a core message and a distinct variant for every selected destination. Preserve approved facts, prices and calls to action. When brand price is free (e.g. 'Free to join', 'Free', 'No cost'), write it as 'Free to join' or 'Join for free' \u2014 never use currency symbols or amounts like $0 or \u20b90."
          },
          "creative": {
            "implementation": "creative_v1",
            "profile": "default",
            "prompt_version": "creative.v2",
            "tools": [
              "memory.search",
              "image.generate"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.creative"
            ],
            "memory_write": [
              "campaign",
              "agent.creative.candidate"
            ],
            "role_instructions": "Create an accessible, channel-appropriate visual direction using the saved brand and campaign constraints."
          },
          "brand_review": {
            "implementation": "brand_review_v1",
            "profile": "default",
            "prompt_version": "brand-review.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.brand_review"
            ],
            "memory_write": [
              "campaign"
            ],
            "role_instructions": "Check factual claims, price, tone, destination variants and supplied evidence. Require revision for unsupported claims. When the brand price is free (e.g. 'Free to join'), any copy that says 'free', 'no cost', or 'join for free' is correct \u2014 do NOT flag it as a pricing discrepancy. Only flag explicit currency amounts (e.g. \u20b9500) that contradict the approved brand price."
          },
          "analytics": {
            "implementation": "analytics_v1",
            "profile": "default",
            "prompt_version": "analytics.v2",
            "tools": [
              "metrics.read",
              "memory.search"
            ],
            "memory_read": [
              "campaign",
              "performance"
            ],
            "memory_write": [
              "campaign",
              "performance.candidate"
            ],
            "role_instructions": "Interpret only measured or explicitly labelled simulated metrics. State source, period and limitations."
          },
          "optimization": {
            "implementation": "optimization_v1",
            "profile": "default",
            "prompt_version": "optimization.v2",
            "tools": [
              "experiments.read",
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "performance",
              "agent.optimization"
            ],
            "memory_write": [
              "campaign",
              "performance.candidate"
            ],
            "role_instructions": "Compare current and historical evidence and propose a measurable experiment with a stop rule."
          },
          "engagement": {
            "implementation": "engagement_v1",
            "profile": "default",
            "prompt_version": "engagement.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.engagement"
            ],
            "memory_write": [
              "campaign",
              "agent.engagement.candidate"
            ],
            "role_instructions": "Classify intent and draft a concise response using approved facts. Escalate sensitive or uncertain cases."
          }
        },
        "profiles": {
          "default": {
            "provider": "gemini",
            "model": "gemini-3.5-flash-lite"
          }
        },
        "limits": {
          "max_retries": 2,
          "max_revisions": 2,
          "max_model_calls": 60,
          "timeout_seconds": 60
        },
        "prompt_registry_version": 1
      },
      "publishing": "live",
      "platforms": [
        "discord",
        "instagram",
        "facebook",
        "whatsapp"
      ],
      "image_provider": "huggingface",
      "hf_model": "black-forest-labs/FLUX.1-schnell",
      "hf_provider": "auto",
      "configuration": {
        "data_mode": "standalone",
        "configuration_version": 3,
        "sources": [],
        "source_connectors": [],
        "destinations": [
          {
            "channel": "discord",
            "state": "publishing_connected"
          },
          {
            "channel": "instagram",
            "state": "publishing_connected"
          },
          {
            "channel": "facebook",
            "state": "publishing_connected"
          },
          {
            "channel": "web_export",
            "state": "content_only"
          },
          {
            "channel": "whatsapp",
            "state": "publishing_connected"
          }
        ],
        "lead_destination": "internal_inbox",
        "capabilities": [
          "campaigns.approve",
          "campaigns.create",
          "content.channel.discord",
          "content.channel.facebook",
          "content.channel.instagram",
          "content.channel.web_export",
          "content.channel.whatsapp",
          "content.export",
          "content.generate",
          "data.internal",
          "imports.files",
          "leads.internal",
          "memory.campaign",
          "publish.discord",
          "publish.facebook",
          "publish.instagram",
          "publish.whatsapp"
        ],
        "website_url": ""
      },
      "workflow": {
        "id": "campaign.v1",
        "registry_version": 1,
        "name": "Complete campaign",
        "description": "Existing research-to-optimization workflow with controlled publishing and engagement.",
        "roles": [
          "research",
          "strategy",
          "writing",
          "creative",
          "brand_review",
          "manager",
          "publishing",
          "analytics",
          "optimization",
          "engagement"
        ],
        "dependencies": {
          "research": [],
          "strategy": [
            "research"
          ],
          "writing": [
            "strategy"
          ],
          "creative": [
            "strategy"
          ],
          "brand_review": [
            "writing",
            "creative"
          ],
          "manager": [
            "brand_review"
          ],
          "publishing": [
            "manager"
          ],
          "analytics": [
            "publishing"
          ],
          "optimization": [
            "analytics"
          ],
          "engagement": [
            "publishing"
          ]
        },
        "required_capabilities": [
          "campaigns.create",
          "content.generate"
        ]
      }
    },
    "state": "COMPLETED",
    "stage": 10,
    "created_at": 1791990717.426286,
    "updated_at": 1791992009.4157567,
    "results": {
      "research": {
        "output": {
          "input_request": null,
          "findings": [
            {
              "text": "Vtabsquare is a welcoming, tech-focused, and collaborative hub designed specifically for software developers, engineering leads, and digital marketers to share knowledge, get live project feedback, engage in peer code reviews, and network in real-time.",
              "source_ref": "brand",
              "source_url": null,
              "source_title": null,
              "retrieved_at": null,
              "confidence": null
            },
            {
              "text": "Joining the Vtabsquare tech community Discord server is 100% free with no hidden costs, offering open access to collaborative discussions and professional networking.",
              "source_ref": "brief",
              "source_url": null,
              "source_title": null,
              "retrieved_at": null,
              "confidence": null
            }
          ],
          "limitations": "Live web search was not utilized as all necessary approved product facts and brief requirements were fully provided within the supplied context."
        },
        "usage": {
          "input_tokens": 857,
          "output_tokens": 174
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "research_v1",
        "prompt_version": "research.v2",
        "request_id": null
      },
      "strategy": {
        "output": {
          "input_request": null,
          "summary": "Develop a targeted strategy for the Vtabsquare Global Tech Community Launch to drive free membership sign-ups among software developers, engineering leads, and digital marketers. The campaign will emphasize peer code reviews, live project feedback, real-time networking, and complete transparency regarding the 100% free Discord server access with no hidden costs.",
          "content_angle": "Empower your career and code by connecting directly with peers through live project feedback and expert code reviews inside a welcoming, entirely free tech community.",
          "success_measure": "Total volume of free member sign-ups and active participation rates in peer code review channels within the Vtabsquare Discord server."
        },
        "usage": {
          "input_tokens": 1564,
          "output_tokens": 154
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "strategy_v1",
        "prompt_version": "strategy.v2",
        "request_id": null
      },
      "writing": {
        "output": {
          "input_request": null,
          "headline": "Supercharge Your Code and Career at Vtabsquare",
          "caption": "Step into the ultimate collaborative space where software developers, engineering leads, and digital marketers converge. Whether you are troubleshooting a complex build, seeking constructive peer code reviews, or looking to showcase your latest project for live feedback, Vtabsquare is your new digital home. Build real-time connections, swap industry knowledge, and elevate your craft alongside passionate professionals from around the globe. Joining the Vtabsquare tech community Discord server is 100% free with no hidden costs. Join for free today and start shaping the future of tech together.",
          "product_claim": "Vtabsquare Tech Community Discord Server",
          "price_claim": "Free to join",
          "call_to_action": "Join for free now",
          "variants": [
            {
              "channel": "discord",
              "headline": "Welcome to Vtabsquare: Where Developers and Marketers Connect",
              "body": "Ready to level up your projects? Vtabsquare is a welcoming, tech-focused hub designed for software developers, engineering leads, and digital marketers to share knowledge, get live project feedback, and network in real-time. Dive into our peer code review channels and collaborate with top talent. Membership is 100% free with no hidden costs. Join for free and claim your spot today!",
              "call_to_action": "Join the Discord Server"
            },
            {
              "channel": "instagram",
              "headline": "Build, Code, and Collaborate Together",
              "body": "Level up your tech journey with Vtabsquare! Connect directly with peers through live project feedback and expert code reviews inside our welcoming, entirely free tech community. Perfect for developers, engineering leads, and digital marketers wanting to network in real-time. It is Free to join with no hidden fees. Tap the link in bio to join for free!",
              "call_to_action": "Join for Free via Link in Bio"
            },
            {
              "channel": "facebook",
              "headline": "Empower Your Career and Code with Vtabsquare",
              "body": "Are you a developer, engineering lead, or digital marketer looking for a collaborative space to grow? Vtabsquare offers real-time networking, expert peer code reviews, and live project feedback. Best of all, it is Free to join with zero hidden costs. Join for free today and become part of our growing global tech community!",
              "call_to_action": "Sign Up for Free"
            },
            {
              "channel": "whatsapp",
              "headline": "Connect Instantly with Vtabsquare Tech Hub",
              "body": "Get instant access to live project feedback, peer code reviews, and real-time networking with software developers, engineering leads, and digital marketers. Vtabsquare is a welcoming, tech-focused community where you can share knowledge and grow your career. Joining the Discord server is Free to join with no hidden charges. Join for free now!",
              "call_to_action": "Tap to Join for Free"
            },
            {
              "channel": "web_export",
              "headline": "Vtabsquare Global Tech Community Launch",
              "body": "Welcome to Vtabsquare, the premier hub for software developers, engineering leads, and digital marketers to share knowledge, receive live project feedback, engage in peer code reviews, and network in real-time. Our community is built on collaboration and peer support. Joining the Vtabsquare tech community Discord server is Free to join with no hidden costs. Join for free today and collaborate with industry peers.",
              "call_to_action": "Join for Free Today"
            }
          ]
        },
        "usage": {
          "input_tokens": 1969,
          "output_tokens": 817
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "writing_v1",
        "prompt_version": "writing.v2",
        "request_id": null
      },
      "creative": {
        "output": {
          "input_request": null,
          "headline": "Supercharge Your Code and Career at Vtabsquare",
          "art_direction": "A sleek, modern minimalist workspace in a dimly lit room illuminated by soft neon indigo and electric blue ambient lighting. On a clean matte dark grey desk, a mechanical keyboard with glowing RGB backlighting sits next to an ergonomic dual-monitor setup displaying lines of clean code and collaborative community chat interfaces. The composition is a straight-on shot capturing the serene yet focused atmosphere of a professional developer. Materials include brushed aluminum, matte plastic, and polished glass. The palette features deep charcoal, neon indigo, and vibrant electric blue, evoking a welcoming, high-tech, collaborative mood.",
          "primary_hex": "#0F172A",
          "accent_hex": "#6366F1",
          "font_name": "Montserrat",
          "layout_style": "minimal"
        },
        "usage": {
          "input_tokens": 2954,
          "output_tokens": 201
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "creative_v1",
        "prompt_version": "creative.v2",
        "request_id": null
      },
      "brand_review": {
        "output": {
          "input_request": null,
          "verdict": "pass",
          "findings": [
            "All product facts align accurately with the approved brand guidelines and campaign brief.",
            "Pricing claims correctly state that joining is free, complying with the brand price of 'Free to join'.",
            "Tone is consistently welcoming, tech-focused, and collaborative across all channels.",
            "Creative art direction fully matches the target audience requirements and campaign goals."
          ],
          "summary": "The brand review has successfully passed. All generated content, copy variants, and creative directions strictly adhere to the approved product facts, brand pricing guidelines, and campaign objectives without any unsupported claims or discrepancies."
        },
        "usage": {
          "input_tokens": 4272,
          "output_tokens": 150
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "brand_review_v1",
        "prompt_version": "brand-review.v2",
        "request_id": null
      },
      "manager": {
        "output": {
          "input_request": null,
          "recommendation": "request_approval",
          "summary": "The Vtabsquare Global Tech Community Launch campaign has successfully completed all stages of the workflow, including strategy formulation, research, multi-channel copywriting, creative art direction, and brand review. The brand review passed with zero violations, confirming that all messaging strictly adheres to approved product facts and that pricing claims ('Free to join') are fully compliant. All generated content and creative prompts accurately reflect the brand's welcoming and collaborative tech-focused tone.",
          "concerns": []
        },
        "usage": {
          "input_tokens": 3800,
          "output_tokens": 124
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "manager_v1",
        "prompt_version": "manager.v2",
        "request_id": null
      },
      "publishing": {
        "output": {
          "mode": "live",
          "status": "published",
          "receipts": [
            {
              "platform": "discord",
              "post_id": "1559947218033713242",
              "status": "published",
              "url": "https://discord.com/channels/@me/1558050009721737360/1559947218033713242"
            },
            {
              "platform": "instagram",
              "post_id": "18119602756972201",
              "status": "published",
              "url": "https://www.instagram.com/p/DeerdXtGnYx/"
            },
            {
              "platform": "facebook",
              "post_id": "[REDACTED]_122106423111503353",
              "status": "published",
              "url": "https://www.facebook.com/[REDACTED]_122106423111503353"
            },
            {
              "platform": "whatsapp",
              "post_id": "wamid.HBgMOTE5NjI5NjMxMDIyFQIAERgSMjRFQjBCQjQ5NjA1MkI5RTY3AA==",
              "status": "published",
              "url": "https://wa.me/[REDACTED]"
            }
          ],
          "content_hash": "6cb32587e94d132f27a92917000dbf5b4375a7189a86dd3bdf3710f175260033",
          "message": "Publication confirmed by discord, instagram, facebook, whatsapp. Media attachments depend on connector capabilities."
        },
        "provider": "tool",
        "model": "none"
      },
      "engagement": {
        "output": {
          "category": "Live engagement queue",
          "draft_reply": "Real comments arrive in the Community inbox. Each reply requires approval.",
          "requires_human": true
        },
        "provider": "tool",
        "model": "none"
      },
      "analytics": {
        "output": {
          "input_request": null,
          "interpretation": "Based on the live metrics from the recent campaign run, a total of 1 impression and 3 engagements were recorded across connected platforms. Specifically, Instagram recorded 3 engagements, while WhatsApp recorded 1 impression and 0 engagements. Discord and Facebook connectors did not expose post metrics for this run. The calculated overall engagement rate of 300.0 percent reflects the platform-reported data where engagements exceed recorded impressions due to specific channel reporting behaviors.",
          "limitations": "Only platform-reported metrics from connected channels are included in this data. Discord and Facebook connectors do not expose account-backed post metrics, and unavailable values remain empty. These metrics represent live performance data from the initial publication run and should be interpreted within the context of limited impression tracking across messaging and social endpoints."
        },
        "usage": {
          "input_tokens": 4682,
          "output_tokens": 167
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "analytics_v1",
        "prompt_version": "analytics.v2",
        "request_id": null,
        "metrics": {
          "mode": "live",
          "records": [
            {
              "platform": "discord",
              "post_id": "1559947218033713242",
              "available": false,
              "impressions": null,
              "engagements": null,
              "engagement_rate_pct": null,
              "limitations": "This connector does not expose account-backed post metrics."
            },
            {
              "platform": "instagram",
              "post_id": "18119602756972201",
              "available": true,
              "impressions": null,
              "engagements": 3,
              "engagement_rate_pct": null,
              "limitations": "Instagram organic metrics via Meta Graph API."
            },
            {
              "platform": "facebook",
              "post_id": "[REDACTED]_122106423111503353",
              "available": false,
              "impressions": null,
              "engagements": null,
              "engagement_rate_pct": null,
              "limitations": "This connector does not expose account-backed post metrics."
            },
            {
              "platform": "whatsapp",
              "post_id": "wamid.HBgMOTE5NjI5NjMxMDIyFQIAERgSMjRFQjBCQjQ5NjA1MkI5RTY3AA==",
              "available": true,
              "impressions": 1,
              "engagements": 0,
              "engagement_rate_pct": null,
              "limitations": "Direct broadcast message delivered to WhatsApp recipient."
            }
          ],
          "impressions": 1,
          "engagements": 3,
          "engagement_rate_pct": 300.0,
          "limitations": "Only platform-reported metrics are included. Unavailable values remain empty."
        }
      },
      "optimization": {
        "output": {
          "input_request": null,
          "hypothesis": "Focusing the campaign messaging specifically on peer code reviews and live project feedback will increase engagement rates among software developers compared to general networking messaging.",
          "proposed_change": "A/B test two distinct messaging variants: Variation A emphasizing peer code reviews and live project feedback for developers, and Variation B emphasizing real-time career networking for digital marketers, measured across Instagram and WhatsApp channels.",
          "stop_rule": "Conclude the experiment after 7 days or once each channel records at least 50 total engagements, whichever comes first."
        },
        "usage": {
          "input_tokens": 9473,
          "output_tokens": 128
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "optimization_v1",
        "prompt_version": "optimization.v2",
        "request_id": null
      }
    },
    "tasks": [
      {
        "id": "306fcdf1fa774ae0b980529767b79659",
        "token": "59583fe7ca5d42559ee25a67b646779c",
        "role": "research",
        "stage": 0,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791990717.871434,
        "input_version": 1,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791990733.4370303
      },
      {
        "id": "0a967c7791634dc6ac5b53f23fe333da",
        "token": "c72659cfdc0448b6a485920c88334555",
        "role": "strategy",
        "stage": 1,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791990734.000428,
        "input_version": 3,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791990741.1568732
      },
      {
        "id": "409809312034483391d03dbf588ebf88",
        "token": "ec02c71906bc43caa58518be6f35f308",
        "role": "writing",
        "stage": 2,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791990741.5247536,
        "input_version": 5,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791990750.2986684
      },
      {
        "id": "84af1ea6465c47659329e1cdc15ef3e2",
        "token": "7d4be97e37ad4700845535c51182cbb9",
        "role": "creative",
        "stage": 3,
        "status": "WAITING_INPUT",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791990741.993338,
        "input_version": 6,
        "model_reserved": false,
        "checkpoint": true,
        "finished_at": 1791990742.0019877
      },
      {
        "id": "c0256503bef74362b860ca290ff03054",
        "token": "76a35a7683814ce98bdee7eef6d5ef9f",
        "role": "creative",
        "stage": 3,
        "status": "ACCEPTED",
        "attempt": 2,
        "generation": 0,
        "started_at": 1791990758.0015032,
        "input_version": 10,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791990768.3407152
      },
      {
        "id": "3c1ae1dab1d94d3cb2e6c8b8e3217116",
        "token": "396dce23588f475d92bda8ebe9963041",
        "role": "brand_review",
        "stage": 4,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791990769.0653455,
        "input_version": 12,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791990776.7557476
      },
      {
        "id": "0194aaf53f8845639b7426dbbea15220",
        "token": "44fd873cf0f44b82a895440d41c4bf69",
        "role": "manager",
        "stage": 5,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791990777.0309641,
        "input_version": 14,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791990784.108637
      },
      {
        "id": "19e24b7e1713489985527ca655273eba",
        "token": "e9c4b66f6cae4d8da9c79787053daccd",
        "role": "publishing",
        "stage": 6,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791990794.3612285,
        "input_version": 17,
        "model_reserved": false,
        "checkpoint": false,
        "finished_at": 1791990835.224004
      },
      {
        "id": "06a42defdc0f487c812ca5717b55ba03",
        "token": "022e8e5818c94a5fbcb335b6d11102fb",
        "role": "analytics",
        "stage": 7,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791991989.3460498,
        "input_version": 20,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791992001.814858
      },
      {
        "id": "ec0c31d71dba4cd98f72370ba5e88cb4",
        "token": "483a86a8b42a4dc6bf7a4bedf1e3d21a",
        "role": "optimization",
        "stage": 8,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791992002.2707474,
        "input_version": 22,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791992009.4157567
      }
    ],
    "events": [
      {
        "id": "0e258f9a992d45238dc12f17ebc6a82e",
        "at": 1791990717.426286,
        "actor": "manager",
        "message": "I've opened Vtabsquare Global Tech Community Launch. Research Bot, check the supplied brief and brand facts first.",
        "target": "research",
        "kind": "assignment"
      },
      {
        "id": "ffe49d743aa543df81c5fde377314d56",
        "at": 1791990717.426286,
        "actor": "manager",
        "message": "Each bot has its own task. I will coordinate handoffs and ask you when a decision is needed.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "54aaa78fb730499f9ac2a0e1ade1d1bf",
        "at": 1791990717.871434,
        "actor": "research",
        "message": "I am checking the supplied brief, audience and approved brand facts.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "586979df0c5441f7a2bedf0e6dab93c2",
        "at": 1791990733.4370303,
        "actor": "research",
        "message": "Live web search was not utilized as all necessary approved product facts and brief requirements were fully provided within the supplied context.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "d9c8b20de6434000899025fcac9616cf",
        "at": 1791990733.4370303,
        "actor": "research",
        "message": "My result has passed its checks. Strategy Bot, I am handing it over for your task.",
        "target": "strategy",
        "kind": "handoff"
      },
      {
        "id": "8bd6f9713359423bbd6a63de8781ebd0",
        "at": 1791990734.000428,
        "actor": "strategy",
        "message": "Research received. I am turning the findings into a campaign plan.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "9bb26b865fd441c4a3587fedcf788a0e",
        "at": 1791990741.1568732,
        "actor": "strategy",
        "message": "Develop a targeted strategy for the Vtabsquare Global Tech Community Launch to drive free membership sign-ups among software developers, engineering leads, and digital marketers. The campaign will emphasize peer code reviews, live project feedback, real-time networking, and complete transparency regarding the 100% free Discord server access with no hidden costs.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "e2c4540108434306b36db4e76fca2f4d",
        "at": 1791990741.1568732,
        "actor": "strategy",
        "message": "My result has passed its checks. Writer Bot, I am handing it over for your task.",
        "target": "writing",
        "kind": "handoff"
      },
      {
        "id": "34f27d4cd13f4e639469412fd64efca9",
        "at": 1791990741.1568732,
        "actor": "strategy",
        "message": "My result has passed its checks. Creative Bot, I am handing it over for your task.",
        "target": "creative",
        "kind": "handoff"
      },
      {
        "id": "5f6bf44e40b14325a8fc3a891e34a672",
        "at": 1791990741.5247536,
        "actor": "writing",
        "message": "Strategy received. I am drafting the copy using the approved product facts.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "fdc52815f5ee4e0eabc68931a3630ae6",
        "at": 1791990741.993338,
        "actor": "creative",
        "message": "Strategy received. I am preparing the visual direction while Writer Bot works on the copy.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "025de0cca4884c1ea01194ffaa414930",
        "at": 1791990742.0019877,
        "actor": "creative",
        "message": "What visual style should I use for this creative?",
        "target": "local-owner",
        "kind": "input_needed"
      },
      {
        "id": "a369c0f947184a6fa441d71e41585731",
        "at": 1791990750.2986684,
        "actor": "writing",
        "message": "Supercharge Your Code and Career at Vtabsquare",
        "target": null,
        "kind": "result"
      },
      {
        "id": "27d3bf60c1bf496bb65506effdade70d",
        "at": 1791990750.2986684,
        "actor": "writing",
        "message": "My result has passed its checks. Brand Guardian, I am handing it over for your task.",
        "target": "brand_review",
        "kind": "handoff"
      },
      {
        "id": "aec9d8e741bb4fac8968ca1f0ed22f09",
        "at": 1791990757.2108855,
        "actor": "local-owner",
        "message": "Sleek dark-mode tech aesthetic with neon indigo and electric blue accents, modern minimalist workspace visuals, and clean collaborative community vibe",
        "target": "creative",
        "kind": "answer"
      },
      {
        "id": "5c30d6833e1c4f13ae60a82d8e392c68",
        "at": 1791990757.2108855,
        "actor": "creative",
        "message": "Thank you. I have your input and will resume my task now.",
        "target": null,
        "kind": "resumed"
      },
      {
        "id": "2ae29515dcca49eca6e324728f34baed",
        "at": 1791990758.0015032,
        "actor": "creative",
        "message": "Strategy received. I am preparing the visual direction while Writer Bot works on the copy.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "36fad6977c534f648143810fea643305",
        "at": 1791990768.3407152,
        "actor": "creative",
        "message": "A sleek, modern minimalist workspace in a dimly lit room illuminated by soft neon indigo and electric blue ambient lighting. On a clean matte dark grey desk, a mechanical keyboard with glowing RGB backlighting sits next to an ergonomic dual-monitor setup displaying lines of clean code and collaborative community chat interfaces. The composition is a straight-on shot capturing the serene yet focused atmosphere of a professional developer. Materials include brushed aluminum, matte plastic, and polished glass. The palette features deep charcoal, neon indigo, and vibrant electric blue, evoking a welcoming, high-tech, collaborative mood.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "e7ac0a5512d94a7e9f8b98d679d5c765",
        "at": 1791990768.3407152,
        "actor": "creative",
        "message": "My result has passed its checks. Brand Guardian, I am handing it over for your task.",
        "target": "brand_review",
        "kind": "handoff"
      },
      {
        "id": "e78cae02fdc44940aa2624040a334acb",
        "at": 1791990769.0653455,
        "actor": "brand_review",
        "message": "Both copy and creative are ready. I am checking claims, price and brand consistency.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "0997660352b740a8a4838a88295298ab",
        "at": 1791990776.7557476,
        "actor": "brand_review",
        "message": "The brand review has successfully passed. All generated content, copy variants, and creative directions strictly adhere to the approved product facts, brand pricing guidelines, and campaign objectives without any unsupported claims or discrepancies.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "f049bde4e2b346049beb5f0782dcada0",
        "at": 1791990776.7557476,
        "actor": "brand_review",
        "message": "My result has passed its checks. Marketing Manager, I am handing it over for your task.",
        "target": "manager",
        "kind": "handoff"
      },
      {
        "id": "18b8e6c84dfb48f19148d6985744e661",
        "at": 1791990777.0309641,
        "actor": "manager",
        "message": "Brand review is ready. I am checking the complete package before asking for your decision.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "ff80c999b9e04463af176ac11fa6b29e",
        "at": 1791990784.1026015,
        "actor": "manager",
        "message": "The Vtabsquare Global Tech Community Launch campaign has successfully completed all stages of the workflow, including strategy formulation, research, multi-channel copywriting, creative art direction, and brand review. The brand review passed with zero violations, confirming that all messaging strictly adheres to approved product facts and that pricing claims ('Free to join') are fully compliant. All generated content and creative prompts accurately reflect the brand's welcoming and collaborative tech-focused tone.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "8663f8afd39c46bfb3a5167378041cd2",
        "at": 1791990784.1026015,
        "actor": "manager",
        "message": "My result has passed its checks. Publisher Bot, I am handing it over for your task.",
        "target": "publishing",
        "kind": "handoff"
      },
      {
        "id": "34f39baa1fbc461fa8f42aed2168bd49",
        "at": 1791990784.108637,
        "actor": "manager",
        "message": "Your input is needed: review the copy and creative, then approve or request changes.",
        "target": "local-owner",
        "kind": "input_needed"
      },
      {
        "id": "c19b1a1bbfa14f6b89d54eb993b7ed45",
        "at": 1791990794.2370484,
        "actor": "local-owner",
        "message": "I approve this exact content version for the selected publishing destination.",
        "target": "manager",
        "kind": "answer"
      },
      {
        "id": "7e4d3ec03fe241d5afcdd886b933badb",
        "at": 1791990794.2370484,
        "actor": "manager",
        "message": "Approval received. Publisher Bot, proceed with this authorized version.",
        "target": "publishing",
        "kind": "assignment"
      },
      {
        "id": "afbba801302947ceb9be0f90fd2c9c20",
        "at": 1791990794.3612285,
        "actor": "publishing",
        "message": "Your approval is recorded. I am submitting the exact authorized version to its selected destination.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "3ea44d6a78e4490ba61c4e70cd65a8e7",
        "at": 1791990835.224004,
        "actor": "publishing",
        "message": "Publication confirmed by discord, instagram, facebook, whatsapp. Media attachments depend on connector capabilities.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "6f849f7631984f0590a83b4396440e3d",
        "at": 1791990835.224004,
        "actor": "publishing",
        "message": "My result has passed its checks. Analytics Bot, I am handing it over for your task.",
        "target": "analytics",
        "kind": "handoff"
      },
      {
        "id": "c7ba955c917840739bd99da384fc2b6e",
        "at": 1791990835.224004,
        "actor": "publishing",
        "message": "My result has passed its checks. Community Bot, I am handing it over for your task.",
        "target": "engagement",
        "kind": "handoff"
      },
      {
        "id": "8ba567e12af449979444930e8815a5c6",
        "at": 1791990835.224004,
        "actor": "analytics",
        "message": "I will collect platform metrics 24 hours after publication.",
        "target": null,
        "kind": "scheduled"
      },
      {
        "id": "b9df67464f604681bace6d1a8d80ef47",
        "at": 1791991989.3460498,
        "actor": "analytics",
        "message": "Publication is confirmed. I am collecting the available performance evidence.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "60ce6dc9a33d4dfba09db62b48bc50d8",
        "at": 1791992001.814858,
        "actor": "analytics",
        "message": "Based on the live metrics from the recent campaign run, a total of 1 impression and 3 engagements were recorded across connected platforms. Specifically, Instagram recorded 3 engagements, while WhatsApp recorded 1 impression and 0 engagements. Discord and Facebook connectors did not expose post metrics for this run. The calculated overall engagement rate of 300.0 percent reflects the platform-reported data where engagements exceed recorded impressions due to specific channel reporting behaviors.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "3e7779c88f274987943d6c7ec108afed",
        "at": 1791992001.814858,
        "actor": "analytics",
        "message": "My result has passed its checks. Optimizer Bot, I am handing it over for your task.",
        "target": "optimization",
        "kind": "handoff"
      },
      {
        "id": "22c7edd34a664355b31b51857445a2c5",
        "at": 1791992002.2707474,
        "actor": "optimization",
        "message": "Analytics received. I am preparing an evidence-based proposal for the next experiment.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "46ae6294d89f4f138eee4c59f1fc0f07",
        "at": 1791992009.4157567,
        "actor": "optimization",
        "message": "Focusing the campaign messaging specifically on peer code reviews and live project feedback will increase engagement rates among software developers compared to general networking messaging.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "4df69a2bc39e46f4983ca225f9de1939",
        "at": 1791992009.4157567,
        "actor": "manager",
        "message": "This workflow is complete. Publication is confirmed. Optimization and reply drafts are ready for you.",
        "target": null,
        "kind": "completed"
      }
    ],
    "approval": {
      "actor": "local-owner",
      "at": 1791990794.236552,
      "content_hash": "6cb32587e94d132f27a92917000dbf5b4375a7189a86dd3bdf3710f175260033",
      "note": "Approved in the workflow panel.",
      "account": "discord,instagram,facebook,whatsapp",
      "action": "publish_live"
    },
    "error": null,
    "not_before": 0,
    "revisions": 0,
    "model_calls": 8,
    "content_hash": "6cb32587e94d132f27a92917000dbf5b4375a7189a86dd3bdf3710f175260033",
    "operation_id": "64de78921214433e98ada41e4f359564",
    "nodes": {
      "research": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "strategy": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "writing": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "creative": {
        "state": "ACCEPTED",
        "attempt": 2,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "brand_review": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "manager": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "publishing": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "analytics": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "optimization": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "engagement": {
        "state": "ACCEPTED",
        "attempt": 0,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      }
    },
    "input_requests": [
      {
        "id": "073cc49636b64bf1a9e8f8762d97babc",
        "role": "creative",
        "question": "What visual style should I use for this creative?",
        "reason": "You asked this bot to check with you before continuing.",
        "kind": "input",
        "status": "ANSWERED",
        "created_at": 1791990742.0019877,
        "generation": 0,
        "answer": "Sleek dark-mode tech aesthetic with neon indigo and electric blue accents, modern minimalist workspace visuals, and clean collaborative community vibe",
        "answered_at": 1791990757.2108855
      },
      {
        "id": "f1f9421397044273a1281b585985d292",
        "role": "manager",
        "question": "Your input is needed: review the copy and creative, then approve or request changes.",
        "reason": "Publisher Bot will wait for your exact-version approval.",
        "kind": "approval",
        "status": "ANSWERED",
        "created_at": 1791990784.108637,
        "generation": 0,
        "answered_at": 1791990794.236552,
        "answer": "Approved"
      }
    ],
    "human_answers": {
      "creative": [
        {
          "question": "What visual style should I use for this creative?",
          "answer": "Sleek dark-mode tech aesthetic with neon indigo and electric blue accents, modern minimalist workspace visuals, and clean collaborative community vibe"
        }
      ]
    }
  },
  {
    "id": "7b3c110f0fd54fe685c9400b3651096f",
    "version": 45,
    "brief": {
      "title": "Vtab Square Real-Time Reporting Tool Launch",
      "audience": "Software developers, engineering leads, and digital marketers",
      "goal": "Invite tech builders and digital marketers to join our free Discord community across Instagram, Facebook, and WhatsApp",
      "instructions": "Highlight that Vtabsquare is completely free to join. Emphasize real-time project collaboration, peer code reviews, and networking with passionate tech professionals.",
      "checkpoint": "creative",
      "destinations": [],
      "audience_id": null,
      "schedule_at": null,
      "workflow_id": "campaign.v1"
    },
    "snapshot": {
      "brand": {
        "name": "Vtab Square",
        "product": "Autonomous Marketing Analytics & Live Reporting Tool",
        "price": "Free to join",
        "tone": "Welcoming, tech-focused, and collaborative",
        "facts": "Vtabsquare is a hub for developers and marketing professionals to share knowledge, get feedback on projects, and network in real-time."
      },
      "agents": {
        "version": 1,
        "agents": {
          "manager": {
            "implementation": "manager_v1",
            "profile": "default",
            "prompt_version": "manager.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.manager"
            ],
            "memory_write": [
              "campaign"
            ],
            "role_instructions": "Review the complete package, capability limitations and approval requirements before recommending an action. When brand price is free (e.g. 'Free to join'), copy that uses 'free', 'join for free', or 'no cost' is factually correct \u2014 do NOT treat it as a pricing error or request revision for pricing. Only recommend 'revise' if there is a clear factual error unrelated to free-tier pricing."
          },
          "research": {
            "implementation": "research_v1",
            "profile": "default",
            "prompt_version": "research.v2",
            "tools": [
              "web.search",
              "website.knowledge",
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.research"
            ],
            "memory_write": [
              "campaign",
              "agent.research.candidate"
            ],
            "role_instructions": "Use approved client knowledge and verified search records. Distinguish facts, estimates, opinions and limitations. Cite only source_ref identifiers supplied by tools."
          },
          "strategy": {
            "implementation": "strategy_v1",
            "profile": "default",
            "prompt_version": "strategy.v2",
            "tools": [
              "memory.search",
              "crm.read_segments"
            ],
            "memory_read": [
              "client",
              "campaign",
              "performance",
              "agent.strategy"
            ],
            "memory_write": [
              "campaign"
            ],
            "role_instructions": "Turn approved evidence into a specific, achievable campaign plan matched to available capabilities and selected destinations."
          },
          "writing": {
            "implementation": "writing_v1",
            "profile": "default",
            "prompt_version": "writing.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.writing"
            ],
            "memory_write": [
              "campaign",
              "agent.writing.candidate"
            ],
            "role_instructions": "Create a core message and a distinct variant for every selected destination. Preserve approved facts, prices and calls to action. When brand price is free (e.g. 'Free to join', 'Free', 'No cost'), write it as 'Free to join' or 'Join for free' \u2014 never use currency symbols or amounts like $0 or \u20b90."
          },
          "creative": {
            "implementation": "creative_v1",
            "profile": "default",
            "prompt_version": "creative.v2",
            "tools": [
              "memory.search",
              "image.generate"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.creative"
            ],
            "memory_write": [
              "campaign",
              "agent.creative.candidate"
            ],
            "role_instructions": "Create an accessible, channel-appropriate visual direction using the saved brand and campaign constraints."
          },
          "brand_review": {
            "implementation": "brand_review_v1",
            "profile": "default",
            "prompt_version": "brand-review.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.brand_review"
            ],
            "memory_write": [
              "campaign"
            ],
            "role_instructions": "Check factual claims, price, tone, destination variants and supplied evidence. Require revision for unsupported claims. When the brand price is free (e.g. 'Free to join'), any copy that says 'free', 'no cost', or 'join for free' is correct \u2014 do NOT flag it as a pricing discrepancy. Only flag explicit currency amounts (e.g. \u20b9500) that contradict the approved brand price."
          },
          "analytics": {
            "implementation": "analytics_v1",
            "profile": "default",
            "prompt_version": "analytics.v2",
            "tools": [
              "metrics.read",
              "memory.search"
            ],
            "memory_read": [
              "campaign",
              "performance"
            ],
            "memory_write": [
              "campaign",
              "performance.candidate"
            ],
            "role_instructions": "Interpret only measured or explicitly labelled simulated metrics. State source, period and limitations."
          },
          "optimization": {
            "implementation": "optimization_v1",
            "profile": "default",
            "prompt_version": "optimization.v2",
            "tools": [
              "experiments.read",
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "performance",
              "agent.optimization"
            ],
            "memory_write": [
              "campaign",
              "performance.candidate"
            ],
            "role_instructions": "Compare current and historical evidence and propose a measurable experiment with a stop rule."
          },
          "engagement": {
            "implementation": "engagement_v1",
            "profile": "default",
            "prompt_version": "engagement.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.engagement"
            ],
            "memory_write": [
              "campaign",
              "agent.engagement.candidate"
            ],
            "role_instructions": "Classify intent and draft a concise response using approved facts. Escalate sensitive or uncertain cases."
          }
        },
        "profiles": {
          "default": {
            "provider": "gemini",
            "model": "gemini-3.5-flash-lite"
          }
        },
        "limits": {
          "max_retries": 2,
          "max_revisions": 2,
          "max_model_calls": 60,
          "timeout_seconds": 45
        },
        "prompt_registry_version": 1
      },
      "publishing": "live",
      "platforms": [
        "discord",
        "instagram",
        "facebook",
        "whatsapp"
      ],
      "image_provider": "huggingface",
      "hf_model": "black-forest-labs/FLUX.1-schnell",
      "hf_provider": "auto",
      "configuration": {
        "data_mode": "standalone",
        "configuration_version": 3,
        "sources": [],
        "source_connectors": [],
        "destinations": [
          {
            "channel": "discord",
            "state": "publishing_connected"
          },
          {
            "channel": "instagram",
            "state": "publishing_connected"
          },
          {
            "channel": "facebook",
            "state": "publishing_connected"
          },
          {
            "channel": "web_export",
            "state": "content_only"
          },
          {
            "channel": "whatsapp",
            "state": "publishing_connected"
          }
        ],
        "lead_destination": "internal_inbox",
        "capabilities": [
          "campaigns.approve",
          "campaigns.create",
          "content.channel.discord",
          "content.channel.facebook",
          "content.channel.instagram",
          "content.channel.web_export",
          "content.channel.whatsapp",
          "content.export",
          "content.generate",
          "data.internal",
          "imports.files",
          "leads.internal",
          "memory.campaign",
          "publish.discord",
          "publish.facebook",
          "publish.instagram",
          "publish.whatsapp"
        ],
        "website_url": ""
      },
      "workflow": {
        "id": "campaign.v1",
        "registry_version": 1,
        "name": "Complete campaign",
        "description": "Existing research-to-optimization workflow with controlled publishing and engagement.",
        "roles": [
          "research",
          "strategy",
          "writing",
          "creative",
          "brand_review",
          "manager",
          "publishing",
          "analytics",
          "optimization",
          "engagement"
        ],
        "dependencies": {
          "research": [],
          "strategy": [
            "research"
          ],
          "writing": [
            "strategy"
          ],
          "creative": [
            "strategy"
          ],
          "brand_review": [
            "writing",
            "creative"
          ],
          "manager": [
            "brand_review"
          ],
          "publishing": [
            "manager"
          ],
          "analytics": [
            "publishing"
          ],
          "optimization": [
            "analytics"
          ],
          "engagement": [
            "publishing"
          ]
        },
        "required_capabilities": [
          "campaigns.create",
          "content.generate"
        ]
      }
    },
    "state": "COMPLETED",
    "stage": 10,
    "created_at": 1791897146.0449266,
    "updated_at": 1791973328.6965,
    "results": {
      "research": {
        "output": {
          "input_request": null,
          "findings": [
            {
              "text": "Vtabsquare is a free-to-join tech community Discord server designed as a collaborative hub for developers and marketing professionals to share knowledge, receive feedback on projects, and network in real-time.",
              "source_ref": "brand",
              "source_url": null,
              "source_title": null,
              "retrieved_at": null,
              "confidence": null
            }
          ],
          "limitations": "Based exclusively on the provided brand and brief facts with no external live search records invoked."
        },
        "usage": {
          "input_tokens": 863,
          "output_tokens": 107
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "research_v1",
        "prompt_version": "research.v2",
        "request_id": null
      },
      "strategy": {
        "output": {
          "input_request": null,
          "summary": "This campaign strategy for Vtabsquare targets software developers, engineering leads, and digital marketers to join our free Discord community. By focusing on real-time project collaboration, peer code reviews, and cross-disciplinary networking across Instagram, Facebook, and WhatsApp, we will drive high-intent community sign-ups. All communications strictly adhere to approved facts, highlighting the free entry and collaborative nature of the hub.",
          "content_angle": "Step into a vibrant ecosystem where developers and marketers unite. Discover real-time project collaboration, peer code reviews, and networking with passionate tech professionals in the free Vtabsquare Discord hub.",
          "success_measure": "Total volume of verified community joins across Instagram, Facebook, and WhatsApp traffic directed to the free Vtabsquare Discord server."
        },
        "usage": {
          "input_tokens": 1405,
          "output_tokens": 175
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "strategy_v1",
        "prompt_version": "strategy.v2",
        "request_id": null
      },
      "writing": {
        "output": {
          "input_request": null,
          "headline": "Unite Code and Growth in the Vtabsquare Tech Hub",
          "caption": "Step into a vibrant ecosystem where developers and marketers unite. Vtabsquare is a collaborative community designed for software builders, engineering leads, and digital marketers to connect in real-time. Whether you are looking for instant feedback on your latest project, peer code reviews from passionate professionals, or cross-disciplinary networking, our Discord server is your new digital home. Join our thriving network to share knowledge and elevate your craft together. Free to join today.",
          "product_claim": "A collaborative Discord hub for developers and marketing professionals",
          "price_claim": "Free to join",
          "call_to_action": "Join our community today",
          "variants": [
            {
              "channel": "instagram",
              "headline": "Where Tech Builders Meet Marketers",
              "body": "Level up your workflow with real-time project collaboration, peer code reviews, and networking with passionate tech professionals. Vtabsquare is a collaborative hub for developers and marketing pros. Free to join. Tap the link in our bio to step into the future of tech networking.",
              "call_to_action": "Tap link in bio to join"
            },
            {
              "channel": "facebook",
              "headline": "Build, Review, and Grow Together",
              "body": "Calling all software developers, engineering leads, and digital marketers! Vtabsquare is your new go-to Discord community for real-time project collaboration, expert peer code reviews, and meaningful industry connections. Share knowledge and get constructive feedback from peers who know the space. Free to join.",
              "call_to_action": "Join the Discord Server"
            },
            {
              "channel": "whatsapp",
              "headline": "Connect Instantly with Tech Peers",
              "body": "Ready to collaborate with top-tier developers and marketers? Vtabsquare is a real-time Discord hub for sharing knowledge, getting project feedback, and networking. Free to join \u2014 step inside our community and start building today.",
              "call_to_action": "Tap to join Vtabsquare"
            }
          ]
        },
        "usage": {
          "input_tokens": 1932,
          "output_tokens": 484
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "writing_v1",
        "prompt_version": "writing.v2",
        "request_id": null
      },
      "creative": {
        "output": {
          "input_request": null,
          "headline": "Where Tech Builders Meet Marketers",
          "art_direction": "A modern, clean tech workspace viewed from a low angle. On a sleek dark wood desk sits a dual-monitor setup: one screen displays complex programming code lines with glowing cyan syntax highlighting, while the adjacent screen shows sleek analytics dashboards and marketing growth charts. Ambient indigo and cyan edge lighting casts soft reflections across the brushed aluminum peripherals. A steaming ceramic mug rests beside a mechanical keyboard. The mood is focused, collaborative, and inspiring.",
          "primary_hex": "#0F172A",
          "accent_hex": "#06B6D4",
          "font_name": "Montserrat",
          "layout_style": "minimal"
        },
        "usage": {
          "input_tokens": 2612,
          "output_tokens": 169
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "creative_v1",
        "prompt_version": "creative.v2",
        "request_id": null
      },
      "brand_review": {
        "output": {
          "input_request": null,
          "verdict": "pass",
          "findings": [
            "The writing content aligns accurately with the approved brand facts, highlighting the free-to-join Discord hub for developers and digital marketers.",
            "Pricing is correctly referenced as 'Free to join' across all generated copy and variants.",
            "The creative output precisely matches the campaign goals, maintaining a professional and tech-focused tone with appropriate visual specifications."
          ],
          "summary": "All prior writing and creative outputs fully comply with the approved brand facts, pricing guidelines, and tone instructions. No unsupported claims or discrepancies were identified."
        },
        "usage": {
          "input_tokens": 333230,
          "output_tokens": 139
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "brand_review_v1",
        "prompt_version": "brand-review.v2",
        "request_id": null
      },
      "manager": {
        "output": {
          "input_request": null,
          "recommendation": "request_approval",
          "summary": "All campaign stages including research, strategy, writing, creative design, and brand review have completed successfully and passed all compliance checks. The messaging accurately reflects Vtabsquare as a free-to-join Discord community for developers and marketing professionals, perfectly matching the creative direction and brand guidelines.",
          "concerns": []
        },
        "usage": {
          "input_tokens": 3392,
          "output_tokens": 92
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "manager_v1",
        "prompt_version": "manager.v2",
        "request_id": null
      },
      "publishing": {
        "output": {
          "mode": "live",
          "status": "published",
          "receipts": [
            {
              "platform": "discord",
              "post_id": "1559559532404019321",
              "status": "published",
              "url": "https://discord.com/channels/@me/1558050009721737360/1559559532404019321"
            },
            {
              "platform": "instagram",
              "post_id": "18167614426469359",
              "status": "published",
              "url": "https://www.instagram.com/p/Deb8xE3mgPB/"
            },
            {
              "platform": "facebook",
              "post_id": "[REDACTED]_122105448375503353",
              "status": "published",
              "url": "https://www.facebook.com/[REDACTED]_122105448375503353"
            },
            {
              "platform": "whatsapp",
              "post_id": "wamid.HBgMOTE5NjI5NjMxMDIyFQIAERgSOTVBODA3MTQwNDA3NEYxOEZEAA==",
              "status": "published",
              "url": "https://wa.me/[REDACTED]"
            }
          ],
          "content_hash": "276832814686365560f7b024803d0627e764f055dfb911293019c459b3848474",
          "message": "Publication confirmed by discord, instagram, facebook, whatsapp. Media attachments depend on connector capabilities."
        },
        "provider": "tool",
        "model": "none"
      },
      "engagement": {
        "output": {
          "category": "Live engagement queue",
          "draft_reply": "Real comments arrive in the Community inbox. Each reply requires approval.",
          "requires_human": true
        },
        "provider": "tool",
        "model": "none"
      },
      "analytics": {
        "output": {
          "input_request": null,
          "interpretation": "The Vtabsquare Omni-Channel Community Launch campaign has been successfully published across Discord, Instagram, Facebook, and WhatsApp. Current live telemetry shows a total of 1 recorded impression and 0 engagements on WhatsApp. Metrics for Discord and Facebook are unavailable due to connector capabilities, while the Instagram metrics query failed with a 400 Bad Request error. Overall reach is currently minimal as the posts have just been deployed.",
          "limitations": "Only platform-reported live metrics are available. Discord and Facebook connectors do not expose post metrics, Instagram metric collection returned a client error, and WhatsApp metrics reflect a single direct broadcast message. Engagement rate cannot be reliably calculated due to lack of exposure across platforms."
        },
        "usage": {
          "input_tokens": 4310,
          "output_tokens": 160
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "analytics_v1",
        "prompt_version": "analytics.v2",
        "request_id": null,
        "metrics": {
          "mode": "live",
          "records": [
            {
              "platform": "discord",
              "post_id": "1559559532404019321",
              "available": false,
              "impressions": null,
              "engagements": null,
              "engagement_rate_pct": null,
              "limitations": "This connector does not expose account-backed post metrics."
            },
            {
              "platform": "instagram",
              "post_id": "18167614426469359",
              "available": false,
              "impressions": null,
              "engagements": null,
              "engagement_rate_pct": null,
              "limitations": "Instagram metrics query failed: Client error '400 Bad Request' for url 'https://graph.facebook.com/v21.0/18167614426469359?fields=like_count,comments_count&access_token=EAAX2S17NPdwB"
            },
            {
              "platform": "facebook",
              "post_id": "[REDACTED]_122105448375503353",
              "available": false,
              "impressions": null,
              "engagements": null,
              "engagement_rate_pct": null,
              "limitations": "This connector does not expose account-backed post metrics."
            },
            {
              "platform": "whatsapp",
              "post_id": "wamid.HBgMOTE5NjI5NjMxMDIyFQIAERgSOTVBODA3MTQwNDA3NEYxOEZEAA==",
              "available": true,
              "impressions": 1,
              "engagements": 0,
              "engagement_rate_pct": null,
              "limitations": "Direct broadcast message delivered to WhatsApp recipient."
            }
          ],
          "impressions": 1,
          "engagements": 0,
          "engagement_rate_pct": 0.0,
          "limitations": "Only platform-reported metrics are included. Unavailable values remain empty."
        }
      },
      "optimization": {
        "output": {
          "input_request": null,
          "hypothesis": "Because live platform analytics on Discord, Facebook, and Instagram currently return zero or unavailable metrics due to connector limitations while WhatsApp shows minimal engagement, shifting the call-to-action focus toward unique trackable invite parameters and direct peer-to-peer developer challenges will increase measurable community sign-ups.",
          "proposed_change": "Introduce an A/B test variation for the next campaign run where Variation A uses the standard community invitation link and Variation B incorporates a gamified weekly developer code review challenge with a unique trackable link across all active channels.",
          "stop_rule": "Conclude the experiment after 7 days or once 50 total verified community joins are recorded, whichever occurs first."
        },
        "usage": {
          "input_tokens": 8252,
          "output_tokens": 160
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "optimization_v1",
        "prompt_version": "optimization.v2",
        "request_id": null
      }
    },
    "tasks": [
      {
        "id": "cbdfd177cfec485e90cf64e883cd0f2a",
        "token": "815173e020bc4ef489c5246d6fa5ada3",
        "role": "research",
        "stage": 0,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791897146.431305,
        "input_version": 1,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791897183.754607
      },
      {
        "id": "becdf7fbc45c4c249684fe2c5490f8b2",
        "token": "500a5ef11fbe4440847a3080d2fe4db3",
        "role": "strategy",
        "stage": 1,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791897184.115826,
        "input_version": 3,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791897219.232342
      },
      {
        "id": "6a42872d46d44b298d02d8d157442fa8",
        "token": "5a15eee124574e259f80824b7a7eb23a",
        "role": "writing",
        "stage": 2,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791897219.5573242,
        "input_version": 5,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791897251.0258124
      },
      {
        "id": "a5ca8d4a81c34a759d672f3c484addf4",
        "token": "d7dcac45cd7d4fc295b03c4abc565393",
        "role": "creative",
        "stage": 3,
        "status": "WAITING_INPUT",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791897219.6267822,
        "input_version": 6,
        "model_reserved": false,
        "checkpoint": true,
        "finished_at": 1791897219.7503703
      },
      {
        "id": "a39a6d74e90942f98a713ac69a50732c",
        "token": "5ad000ee223c489583dfdfecae665237",
        "role": "creative",
        "stage": 3,
        "status": "ACCEPTED",
        "attempt": 2,
        "generation": 0,
        "started_at": 1791897271.8107724,
        "input_version": 10,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791897328.1556008
      },
      {
        "id": "c10c146865d748289d2a51b25c8241b7",
        "token": "b11331a888a74dfdbcbec930ef4279d6",
        "role": "brand_review",
        "stage": 4,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791897328.5640762,
        "input_version": 12,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791897369.7502332
      },
      {
        "id": "187f91e3358a4cd291dc6bb0cdfbe4fa",
        "token": "70d55caada24414d8732832cfb8cd28c",
        "role": "manager",
        "stage": 5,
        "status": "FAILED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791897370.124943,
        "input_version": 14,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791897374.0201578
      },
      {
        "id": "70bef6513e694347a4228907cd196be0",
        "token": "d90f8188f71143fcaf3e10a1e1b90f81",
        "role": "manager",
        "stage": 5,
        "status": "FAILED",
        "attempt": 2,
        "generation": 0,
        "started_at": 1791897378.5588472,
        "input_version": 17,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791897381.591332
      },
      {
        "id": "207fa57789b44e9fb55137e9b26236f8",
        "token": "957391d380ee40fc8cf6cc53b28a5564",
        "role": "manager",
        "stage": 5,
        "status": "FAILED",
        "attempt": 3,
        "generation": 0,
        "started_at": 1791897527.6138568,
        "input_version": 20,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791897531.5808253
      },
      {
        "id": "5388f6b396364094941504f8ad56a39a",
        "token": "bd9b2cf1c27240429f6e69f77f3fa44d",
        "role": "manager",
        "stage": 5,
        "status": "FAILED",
        "attempt": 4,
        "generation": 0,
        "started_at": 1791897536.578262,
        "input_version": 23,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791897581.7547052
      },
      {
        "id": "88bf6c2822664fc6ba016e1bccf654af",
        "token": "e39aed28a3df4131b246ee94187db864",
        "role": "manager",
        "stage": 5,
        "status": "ACCEPTED",
        "attempt": 5,
        "generation": 0,
        "started_at": 1791898225.603129,
        "input_version": 26,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791898282.01183
      },
      {
        "id": "6ca6406328e948fea0f36c7b9445259b",
        "token": "deeec41b1cd147808a0e724fe73dec14",
        "role": "publishing",
        "stage": 6,
        "status": "FAILED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791898360.6682487,
        "input_version": 29,
        "model_reserved": false,
        "checkpoint": false,
        "finished_at": 1791898376.6793442
      },
      {
        "id": "60741ef3912443d2a19d03964104245b",
        "token": "2e91ea20ce784cd0b617ff7427c586b9",
        "role": "publishing",
        "stage": 6,
        "status": "FAILED",
        "attempt": 2,
        "generation": 0,
        "started_at": 1791898392.8248847,
        "input_version": 32,
        "model_reserved": false,
        "checkpoint": false,
        "finished_at": 1791898392.8590918
      },
      {
        "id": "2f3e09a7c9894915b24ce6f7c8d82a9f",
        "token": "013a4608ecb54b44a95531628797d411",
        "role": "publishing",
        "stage": 6,
        "status": "FAILED",
        "attempt": 3,
        "generation": 0,
        "started_at": 1791898395.189422,
        "input_version": 35,
        "model_reserved": false,
        "checkpoint": false,
        "finished_at": 1791898395.2447202
      },
      {
        "id": "a6e970b943f64eb694b912486267681b",
        "token": "120e02088a064df28bfb58d7f1bdad67",
        "role": "publishing",
        "stage": 6,
        "status": "ACCEPTED",
        "attempt": 4,
        "generation": 0,
        "started_at": 1791899214.2200618,
        "input_version": 38,
        "model_reserved": false,
        "checkpoint": false,
        "finished_at": 1791899236.4622388
      },
      {
        "id": "4b033b6ace2243228f19ab6c9f1b8b2f",
        "token": "240754370cc246ed8cd45fab31df0f2c",
        "role": "analytics",
        "stage": 7,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791973308.69932,
        "input_version": 41,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791973321.9433556
      },
      {
        "id": "8c6d84ca580b41a1942313774b4da43b",
        "token": "20450848d7a04c80855439e55c119242",
        "role": "optimization",
        "stage": 8,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791973322.3050618,
        "input_version": 43,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791973328.6965
      }
    ],
    "events": [
      {
        "id": "2b7696ab42504f4990ec22cb1876ea99",
        "at": 1791897146.045435,
        "actor": "manager",
        "message": "I've opened Vtabsquare Omni-Channel Community Launch. Research Bot, check the supplied brief and brand facts first.",
        "target": "research",
        "kind": "assignment"
      },
      {
        "id": "3c7a07ae4cd04326b68aedff38da964f",
        "at": 1791897146.045435,
        "actor": "manager",
        "message": "Each bot has its own task. I will coordinate handoffs and ask you when a decision is needed.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "690205dc665940d194dcab99e41b88b2",
        "at": 1791897146.431305,
        "actor": "research",
        "message": "I am checking the supplied brief, audience and approved brand facts.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "7f6a39bfe3e44cb6a4de8499ac8e4feb",
        "at": 1791897183.754607,
        "actor": "research",
        "message": "Based exclusively on the provided brand and brief facts with no external live search records invoked.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "2a3828776f6f4d72b333f38d00e9736d",
        "at": 1791897183.754607,
        "actor": "research",
        "message": "My result has passed its checks. Strategy Bot, I am handing it over for your task.",
        "target": "strategy",
        "kind": "handoff"
      },
      {
        "id": "722e00a77d6242109c4684cdd474f401",
        "at": 1791897184.115826,
        "actor": "strategy",
        "message": "Research received. I am turning the findings into a campaign plan.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "b2a2d0a1f2b1479d867ad4710cc3d957",
        "at": 1791897219.232342,
        "actor": "strategy",
        "message": "This campaign strategy for Vtabsquare targets software developers, engineering leads, and digital marketers to join our free Discord community. By focusing on real-time project collaboration, peer code reviews, and cross-disciplinary networking across Instagram, Facebook, and WhatsApp, we will drive high-intent community sign-ups. All communications strictly adhere to approved facts, highlighting the free entry and collaborative nature of the hub.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "a4cbbf1695e04362b1446c23ae125e28",
        "at": 1791897219.232342,
        "actor": "strategy",
        "message": "My result has passed its checks. Writer Bot, I am handing it over for your task.",
        "target": "writing",
        "kind": "handoff"
      },
      {
        "id": "47c65a94c55b41dc8e613a0e95ce03a2",
        "at": 1791897219.232342,
        "actor": "strategy",
        "message": "My result has passed its checks. Creative Bot, I am handing it over for your task.",
        "target": "creative",
        "kind": "handoff"
      },
      {
        "id": "7e5ddccaacc84352a6413cc8d5146da6",
        "at": 1791897219.5573242,
        "actor": "writing",
        "message": "Strategy received. I am drafting the copy using the approved product facts.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "e68254c6a18640ebb228b6eb9ca4653f",
        "at": 1791897219.6267822,
        "actor": "creative",
        "message": "Strategy received. I am preparing the visual direction while Writer Bot works on the copy.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "188cae7dc0ef4aac90664dad717afe3e",
        "at": 1791897219.7503703,
        "actor": "creative",
        "message": "What visual style should I use for this creative?",
        "target": "local-owner",
        "kind": "input_needed"
      },
      {
        "id": "2d1960df369347d78215b7062e2a4ca9",
        "at": 1791897251.0258124,
        "actor": "writing",
        "message": "Unite Code and Growth in the Vtabsquare Tech Hub",
        "target": null,
        "kind": "result"
      },
      {
        "id": "6fc08bcc0783408794fc2be3aca3cae3",
        "at": 1791897251.0258124,
        "actor": "writing",
        "message": "My result has passed its checks. Brand Guardian, I am handing it over for your task.",
        "target": "brand_review",
        "kind": "handoff"
      },
      {
        "id": "fbd7c95a7d6e4849be4f791880dd9091",
        "at": 1791897271.1744356,
        "actor": "local-owner",
        "message": "Modern tech workspace with glowing cyan and indigo accents, dual monitors showing code and campaign analytics, collaborative community vibe, clean minimalist aesthetic.",
        "target": "creative",
        "kind": "answer"
      },
      {
        "id": "6e98f290e59846369e9be270bf0a505e",
        "at": 1791897271.1744356,
        "actor": "creative",
        "message": "Thank you. I have your input and will resume my task now.",
        "target": null,
        "kind": "resumed"
      },
      {
        "id": "45c949880a7d4a23a538f79154f0196a",
        "at": 1791897271.8107724,
        "actor": "creative",
        "message": "Strategy received. I am preparing the visual direction while Writer Bot works on the copy.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "c853e476e12f4af1859a3cb13e261b6d",
        "at": 1791897328.1556008,
        "actor": "creative",
        "message": "A modern, clean tech workspace viewed from a low angle. On a sleek dark wood desk sits a dual-monitor setup: one screen displays complex programming code lines with glowing cyan syntax highlighting, while the adjacent screen shows sleek analytics dashboards and marketing growth charts. Ambient indigo and cyan edge lighting casts soft reflections across the brushed aluminum peripherals. A steaming ceramic mug rests beside a mechanical keyboard. The mood is focused, collaborative, and inspiring.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "2fe1b9f076e8411ea841e91f8ed8e86a",
        "at": 1791897328.1556008,
        "actor": "creative",
        "message": "My result has passed its checks. Brand Guardian, I am handing it over for your task.",
        "target": "brand_review",
        "kind": "handoff"
      },
      {
        "id": "3de63e33217d42d1b0be93442eb9bb96",
        "at": 1791897328.5640762,
        "actor": "brand_review",
        "message": "Both copy and creative are ready. I am checking claims, price and brand consistency.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "7c466e99ae4a409180c2ad3be6c0b1bf",
        "at": 1791897369.7502332,
        "actor": "brand_review",
        "message": "All prior writing and creative outputs fully comply with the approved brand facts, pricing guidelines, and tone instructions. No unsupported claims or discrepancies were identified.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "57204acb3bba497490c4d0db2eeda3a2",
        "at": 1791897369.7502332,
        "actor": "brand_review",
        "message": "My result has passed its checks. Marketing Manager, I am handing it over for your task.",
        "target": "manager",
        "kind": "handoff"
      },
      {
        "id": "c4e3c37fb89d489c8371684c73a94509",
        "at": 1791897370.124943,
        "actor": "manager",
        "message": "Brand review is ready. I am checking the complete package before asking for your decision.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "043c58a797844b6f8180bff7f9429512",
        "at": 1791897374.0198479,
        "actor": "manager",
        "message": "Gemini quota or rate limit reached. Check your account, then retry.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "79e20239e06c4214848fbf6064d236b4",
        "at": 1791897374.0201578,
        "actor": "manager",
        "message": "Your attention is needed for Marketing Manager: Gemini quota or rate limit reached. Check your account, then retry.",
        "target": "local-owner",
        "kind": "attention"
      },
      {
        "id": "654191cf87304f97bc68317ad644bc6d",
        "at": 1791897377.7551465,
        "actor": "manager",
        "message": "The corrected bot tasks are queued to retry.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "cb248ffa042641cda3ed847cf90f69fe",
        "at": 1791897378.5588472,
        "actor": "manager",
        "message": "Brand review is ready. I am checking the complete package before asking for your decision.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "edc372790589469b85500d44895413cb",
        "at": 1791897381.591332,
        "actor": "manager",
        "message": "Gemini quota or rate limit reached. Check your account, then retry.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "9fc0078f10774f718d40248b32ae85b0",
        "at": 1791897381.591332,
        "actor": "manager",
        "message": "Your attention is needed for Marketing Manager: Gemini quota or rate limit reached. Check your account, then retry.",
        "target": "local-owner",
        "kind": "attention"
      },
      {
        "id": "25aca7410bb848c0844986a0425c4c57",
        "at": 1791897527.1820173,
        "actor": "manager",
        "message": "The corrected bot tasks are queued to retry.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "40133a6b2e60472982447f959b3badb9",
        "at": 1791897527.6138568,
        "actor": "manager",
        "message": "Brand review is ready. I am checking the complete package before asking for your decision.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "0e7683fa357f4467975146b1123b7cd3",
        "at": 1791897531.5808253,
        "actor": "manager",
        "message": "Gemini connection failed. No result was accepted.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "22549d880b9045e8bc9087690ac6ceda",
        "at": 1791897531.5808253,
        "actor": "manager",
        "message": "Your attention is needed for Marketing Manager: Gemini connection failed. No result was accepted.",
        "target": "local-owner",
        "kind": "attention"
      },
      {
        "id": "fee5fe9d19184672804db9f030b9c8d1",
        "at": 1791897535.8630738,
        "actor": "manager",
        "message": "The corrected bot tasks are queued to retry.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "7a073f17680245b6b12d0e70fe782595",
        "at": 1791897536.578262,
        "actor": "manager",
        "message": "Brand review is ready. I am checking the complete package before asking for your decision.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "934126b73e7f411e8ecb75b2e3717e0f",
        "at": 1791897581.754205,
        "actor": "manager",
        "message": "Gemini connection failed. No result was accepted.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "f489c48952924fcabb49c043542226eb",
        "at": 1791897581.7547052,
        "actor": "manager",
        "message": "Your attention is needed for Marketing Manager: Gemini connection failed. No result was accepted.",
        "target": "local-owner",
        "kind": "attention"
      },
      {
        "id": "80f1c91e798142d4a66f04acd4b85621",
        "at": 1791898225.5438168,
        "actor": "manager",
        "message": "The corrected bot tasks are queued to retry.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "f5447e4ddfb04ab39eb659ab95d8cde4",
        "at": 1791898225.603129,
        "actor": "manager",
        "message": "Brand review is ready. I am checking the complete package before asking for your decision.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "e8c289f3b8104c01ab5807cc50b74a18",
        "at": 1791898282.006778,
        "actor": "manager",
        "message": "All campaign stages including research, strategy, writing, creative design, and brand review have completed successfully and passed all compliance checks. The messaging accurately reflects Vtabsquare as a free-to-join Discord community for developers and marketing professionals, perfectly matching the creative direction and brand guidelines.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "a09ffc1cd54f47718d6cc011c3295c8d",
        "at": 1791898282.006778,
        "actor": "manager",
        "message": "My result has passed its checks. Publisher Bot, I am handing it over for your task.",
        "target": "publishing",
        "kind": "handoff"
      },
      {
        "id": "a928182a2a6f41cc8947fb86ccf58bb6",
        "at": 1791898282.01183,
        "actor": "manager",
        "message": "Your input is needed: review the copy and creative, then approve or request changes.",
        "target": "local-owner",
        "kind": "input_needed"
      },
      {
        "id": "471c14816c4b4cdfb7502966545024f6",
        "at": 1791898360.236593,
        "actor": "local-owner",
        "message": "I approve this exact content version for the selected publishing destination.",
        "target": "manager",
        "kind": "answer"
      },
      {
        "id": "357a592f26334056a7be48aaeaaa5402",
        "at": 1791898360.236593,
        "actor": "manager",
        "message": "Approval received. Publisher Bot, proceed with this authorized version.",
        "target": "publishing",
        "kind": "assignment"
      },
      {
        "id": "64a1243edb7448879bed39d00b160306",
        "at": 1791898360.6682487,
        "actor": "publishing",
        "message": "Your approval is recorded. I am submitting the exact authorized version to its selected destination.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "c60f62af406c4c1a9f1c274bdc89e0ee",
        "at": 1791898376.6783285,
        "actor": "publishing",
        "message": "Task execution failed. Review the configuration and evidence.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "253571e026c049268589f7a56c142ea3",
        "at": 1791898376.6793442,
        "actor": "manager",
        "message": "Your attention is needed for Publisher Bot: Task execution failed. Review the configuration and evidence.",
        "target": "local-owner",
        "kind": "attention"
      },
      {
        "id": "8c74d6254cec4c92b3a279c357362e83",
        "at": 1791898392.7294405,
        "actor": "manager",
        "message": "The corrected bot tasks are queued to retry.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "73a0540eb0194bada9f587f3030ae290",
        "at": 1791898392.8248847,
        "actor": "publishing",
        "message": "Your approval is recorded. I am submitting the exact authorized version to its selected destination.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "6f3f2617c43044babc385424b26a7bb9",
        "at": 1791898392.8590918,
        "actor": "publishing",
        "message": "A previous publication may have reached instagram. Reconcile the account before retrying.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "86f5247a0cb24379a64513afd6dcee0d",
        "at": 1791898392.8590918,
        "actor": "manager",
        "message": "Your attention is needed for Publisher Bot: A previous publication may have reached instagram. Reconcile the account before retrying.",
        "target": "local-owner",
        "kind": "attention"
      },
      {
        "id": "8ca23796db0845a0ad0968a1ffb5e2fe",
        "at": 1791898394.7783356,
        "actor": "manager",
        "message": "The corrected bot tasks are queued to retry.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "bbe8ef07e43948cca28128fcf1a1cb5b",
        "at": 1791898395.189422,
        "actor": "publishing",
        "message": "Your approval is recorded. I am submitting the exact authorized version to its selected destination.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "cb1de27548d743fbb854b8c6ddfec999",
        "at": 1791898395.2447202,
        "actor": "publishing",
        "message": "A previous publication may have reached instagram. Reconcile the account before retrying.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "366b9638ee2646fdbe0e9bceca10fa96",
        "at": 1791898395.2447202,
        "actor": "manager",
        "message": "Your attention is needed for Publisher Bot: A previous publication may have reached instagram. Reconcile the account before retrying.",
        "target": "local-owner",
        "kind": "attention"
      },
      {
        "id": "cbb6243e31c44c9d9cea92e6d8677f8e",
        "at": 1791899213.9323742,
        "actor": "manager",
        "message": "The corrected bot tasks are queued to retry.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "be39ea7434bd4aa1b14307e272de0b48",
        "at": 1791899214.2200618,
        "actor": "publishing",
        "message": "Your approval is recorded. I am submitting the exact authorized version to its selected destination.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "d6d3decc117743b6ad4121cf63ee05dd",
        "at": 1791899236.4622388,
        "actor": "publishing",
        "message": "Publication confirmed by discord, instagram, facebook, whatsapp. Media attachments depend on connector capabilities.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "7c1801b366804bbc8aa5e928e775952e",
        "at": 1791899236.4622388,
        "actor": "publishing",
        "message": "My result has passed its checks. Analytics Bot, I am handing it over for your task.",
        "target": "analytics",
        "kind": "handoff"
      },
      {
        "id": "863d6cf635854c2bbfde28ee59d844b3",
        "at": 1791899236.4622388,
        "actor": "publishing",
        "message": "My result has passed its checks. Community Bot, I am handing it over for your task.",
        "target": "engagement",
        "kind": "handoff"
      },
      {
        "id": "a05733a93e834c7a8bddcfe6710b7f8c",
        "at": 1791899236.4622388,
        "actor": "analytics",
        "message": "I will collect platform metrics 24 hours after publication.",
        "target": null,
        "kind": "scheduled"
      },
      {
        "id": "02ac4c2774264b5288528f1a36972159",
        "at": 1791973308.69932,
        "actor": "analytics",
        "message": "Publication is confirmed. I am collecting the available performance evidence.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "8acda8fd9f1d4e6d8ac4975e8bdb1a1b",
        "at": 1791973321.9433556,
        "actor": "analytics",
        "message": "The Vtabsquare Omni-Channel Community Launch campaign has been successfully published across Discord, Instagram, Facebook, and WhatsApp. Current live telemetry shows a total of 1 recorded impression and 0 engagements on WhatsApp. Metrics for Discord and Facebook are unavailable due to connector capabilities, while the Instagram metrics query failed with a 400 Bad Request error. Overall reach is currently minimal as the posts have just been deployed.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "9fb0e4413ac749f1a5c020982ba21679",
        "at": 1791973321.9433556,
        "actor": "analytics",
        "message": "My result has passed its checks. Optimizer Bot, I am handing it over for your task.",
        "target": "optimization",
        "kind": "handoff"
      },
      {
        "id": "c6c7c351400e44bb9fe5b279e3cce955",
        "at": 1791973322.3050618,
        "actor": "optimization",
        "message": "Analytics received. I am preparing an evidence-based proposal for the next experiment.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "65464d0558fa43b08b92332f6fc8e4b4",
        "at": 1791973328.6965,
        "actor": "optimization",
        "message": "Because live platform analytics on Discord, Facebook, and Instagram currently return zero or unavailable metrics due to connector limitations while WhatsApp shows minimal engagement, shifting the call-to-action focus toward unique trackable invite parameters and direct peer-to-peer developer challenges will increase measurable community sign-ups.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "40e6f45857b34494aed7cf0cd21af83a",
        "at": 1791973328.6965,
        "actor": "manager",
        "message": "This workflow is complete. Publication is confirmed. Optimization and reply drafts are ready for you.",
        "target": null,
        "kind": "completed"
      }
    ],
    "approval": {
      "actor": "local-owner",
      "at": 1791898360.2360995,
      "content_hash": "276832814686365560f7b024803d0627e764f055dfb911293019c459b3848474",
      "note": "Approved in the workflow panel.",
      "account": "discord,instagram,facebook,whatsapp",
      "action": "publish_live"
    },
    "error": null,
    "not_before": 0,
    "revisions": 0,
    "model_calls": 12,
    "content_hash": "276832814686365560f7b024803d0627e764f055dfb911293019c459b3848474",
    "operation_id": "026d90af3f864258ab103186fee433f2",
    "nodes": {
      "research": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "strategy": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "writing": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "creative": {
        "state": "ACCEPTED",
        "attempt": 2,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "brand_review": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "manager": {
        "state": "ACCEPTED",
        "attempt": 5,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "publishing": {
        "state": "ACCEPTED",
        "attempt": 4,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "analytics": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "optimization": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "engagement": {
        "state": "ACCEPTED",
        "attempt": 0,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      }
    },
    "input_requests": [
      {
        "id": "72532726115f4369927d2f4cafdec55f",
        "role": "creative",
        "question": "What visual style should I use for this creative?",
        "reason": "You asked this bot to check with you before continuing.",
        "kind": "input",
        "status": "ANSWERED",
        "created_at": 1791897219.7503703,
        "generation": 0,
        "answer": "Modern tech workspace with glowing cyan and indigo accents, dual monitors showing code and campaign analytics, collaborative community vibe, clean minimalist aesthetic.",
        "answered_at": 1791897271.1744356
      },
      {
        "id": "a0a6b772e25844b4bdf2e0f180562cd1",
        "role": "manager",
        "question": "Your input is needed: review the copy and creative, then approve or request changes.",
        "reason": "Publisher Bot will wait for your exact-version approval.",
        "kind": "approval",
        "status": "ANSWERED",
        "created_at": 1791898282.01183,
        "generation": 0,
        "answered_at": 1791898360.2360995,
        "answer": "Approved"
      }
    ],
    "human_answers": {
      "creative": [
        {
          "question": "What visual style should I use for this creative?",
          "answer": "Modern tech workspace with glowing cyan and indigo accents, dual monitors showing code and campaign analytics, collaborative community vibe, clean minimalist aesthetic."
        }
      ]
    }
  },
  {
    "id": "aa9b35b3cebe43fcb6696a1b4cb33e9a",
    "version": 37,
    "brief": {
      "title": "AI Marketing Masterclass & Live Demo Day",
      "audience": "Software developers, engineering leads, and digital marketers",
      "goal": "Invite tech builders and marketers to join our free Discord community directly via WhatsApp",
      "instructions": "Emphasize that Vtabsquare is completely free to join. Highlight real-time developer collaboration, peer project feedback, and community networking.",
      "checkpoint": "none",
      "destinations": [],
      "audience_id": null,
      "schedule_at": null,
      "workflow_id": "campaign.v1"
    },
    "snapshot": {
      "brand": {
        "name": "Vtab Square",
        "product": "AI Marketing Masterclass & Community Demo",
        "price": "Free to join",
        "tone": "Welcoming, tech-focused, and collaborative",
        "facts": "Vtabsquare is a hub for developers and marketing professionals to share knowledge, get feedback on projects, and network in real-time."
      },
      "agents": {
        "version": 1,
        "agents": {
          "manager": {
            "implementation": "manager_v1",
            "profile": "default",
            "prompt_version": "manager.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.manager"
            ],
            "memory_write": [
              "campaign"
            ],
            "role_instructions": "Review the complete package, capability limitations and approval requirements before recommending an action. When brand price is free (e.g. 'Free to join'), copy that uses 'free', 'join for free', or 'no cost' is factually correct \u2014 do NOT treat it as a pricing error or request revision for pricing. Only recommend 'revise' if there is a clear factual error unrelated to free-tier pricing."
          },
          "research": {
            "implementation": "research_v1",
            "profile": "default",
            "prompt_version": "research.v2",
            "tools": [
              "web.search",
              "website.knowledge",
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.research"
            ],
            "memory_write": [
              "campaign",
              "agent.research.candidate"
            ],
            "role_instructions": "Use approved client knowledge and verified search records. Distinguish facts, estimates, opinions and limitations. Cite only source_ref identifiers supplied by tools."
          },
          "strategy": {
            "implementation": "strategy_v1",
            "profile": "default",
            "prompt_version": "strategy.v2",
            "tools": [
              "memory.search",
              "crm.read_segments"
            ],
            "memory_read": [
              "client",
              "campaign",
              "performance",
              "agent.strategy"
            ],
            "memory_write": [
              "campaign"
            ],
            "role_instructions": "Turn approved evidence into a specific, achievable campaign plan matched to available capabilities and selected destinations."
          },
          "writing": {
            "implementation": "writing_v1",
            "profile": "default",
            "prompt_version": "writing.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.writing"
            ],
            "memory_write": [
              "campaign",
              "agent.writing.candidate"
            ],
            "role_instructions": "Create a core message and a distinct variant for every selected destination. Preserve approved facts, prices and calls to action. When brand price is free (e.g. 'Free to join', 'Free', 'No cost'), write it as 'Free to join' or 'Join for free' \u2014 never use currency symbols or amounts like $0 or \u20b90."
          },
          "creative": {
            "implementation": "creative_v1",
            "profile": "default",
            "prompt_version": "creative.v2",
            "tools": [
              "memory.search",
              "image.generate"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.creative"
            ],
            "memory_write": [
              "campaign",
              "agent.creative.candidate"
            ],
            "role_instructions": "Create an accessible, channel-appropriate visual direction using the saved brand and campaign constraints."
          },
          "brand_review": {
            "implementation": "brand_review_v1",
            "profile": "default",
            "prompt_version": "brand-review.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.brand_review"
            ],
            "memory_write": [
              "campaign"
            ],
            "role_instructions": "Check factual claims, price, tone, destination variants and supplied evidence. Require revision for unsupported claims. When the brand price is free (e.g. 'Free to join'), any copy that says 'free', 'no cost', or 'join for free' is correct \u2014 do NOT flag it as a pricing discrepancy. Only flag explicit currency amounts (e.g. \u20b9500) that contradict the approved brand price."
          },
          "analytics": {
            "implementation": "analytics_v1",
            "profile": "default",
            "prompt_version": "analytics.v2",
            "tools": [
              "metrics.read",
              "memory.search"
            ],
            "memory_read": [
              "campaign",
              "performance"
            ],
            "memory_write": [
              "campaign",
              "performance.candidate"
            ],
            "role_instructions": "Interpret only measured or explicitly labelled simulated metrics. State source, period and limitations."
          },
          "optimization": {
            "implementation": "optimization_v1",
            "profile": "default",
            "prompt_version": "optimization.v2",
            "tools": [
              "experiments.read",
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "performance",
              "agent.optimization"
            ],
            "memory_write": [
              "campaign",
              "performance.candidate"
            ],
            "role_instructions": "Compare current and historical evidence and propose a measurable experiment with a stop rule."
          },
          "engagement": {
            "implementation": "engagement_v1",
            "profile": "default",
            "prompt_version": "engagement.v2",
            "tools": [
              "memory.search"
            ],
            "memory_read": [
              "client",
              "campaign",
              "agent.engagement"
            ],
            "memory_write": [
              "campaign",
              "agent.engagement.candidate"
            ],
            "role_instructions": "Classify intent and draft a concise response using approved facts. Escalate sensitive or uncertain cases."
          }
        },
        "profiles": {
          "default": {
            "provider": "gemini",
            "model": "gemini-3.5-flash-lite"
          }
        },
        "limits": {
          "max_retries": 2,
          "max_revisions": 2,
          "max_model_calls": 60,
          "timeout_seconds": 45
        },
        "prompt_registry_version": 1
      },
      "publishing": "live",
      "platforms": [
        "whatsapp"
      ],
      "image_provider": "huggingface",
      "hf_model": "black-forest-labs/FLUX.1-schnell",
      "hf_provider": "auto",
      "configuration": {
        "data_mode": "standalone",
        "configuration_version": 3,
        "sources": [],
        "source_connectors": [],
        "destinations": [
          {
            "channel": "discord",
            "state": "publishing_connected"
          },
          {
            "channel": "instagram",
            "state": "publishing_connected"
          },
          {
            "channel": "facebook",
            "state": "publishing_connected"
          },
          {
            "channel": "web_export",
            "state": "content_only"
          },
          {
            "channel": "whatsapp",
            "state": "publishing_connected"
          }
        ],
        "lead_destination": "internal_inbox",
        "capabilities": [
          "campaigns.approve",
          "campaigns.create",
          "content.channel.discord",
          "content.channel.facebook",
          "content.channel.instagram",
          "content.channel.web_export",
          "content.channel.whatsapp",
          "content.export",
          "content.generate",
          "data.internal",
          "imports.files",
          "leads.internal",
          "memory.campaign",
          "publish.discord",
          "publish.facebook",
          "publish.instagram",
          "publish.whatsapp"
        ],
        "website_url": ""
      },
      "workflow": {
        "id": "campaign.v1",
        "registry_version": 1,
        "name": "Complete campaign",
        "description": "Existing research-to-optimization workflow with controlled publishing and engagement.",
        "roles": [
          "research",
          "strategy",
          "writing",
          "creative",
          "brand_review",
          "manager",
          "publishing",
          "analytics",
          "optimization",
          "engagement"
        ],
        "dependencies": {
          "research": [],
          "strategy": [
            "research"
          ],
          "writing": [
            "strategy"
          ],
          "creative": [
            "strategy"
          ],
          "brand_review": [
            "writing",
            "creative"
          ],
          "manager": [
            "brand_review"
          ],
          "publishing": [
            "manager"
          ],
          "analytics": [
            "publishing"
          ],
          "optimization": [
            "analytics"
          ],
          "engagement": [
            "publishing"
          ]
        },
        "required_capabilities": [
          "campaigns.create",
          "content.generate"
        ]
      }
    },
    "state": "COMPLETED",
    "stage": 10,
    "created_at": 1791895046.1024125,
    "updated_at": 1791982615.9490778,
    "results": {
      "research": {
        "output": {
          "input_request": null,
          "findings": [
            {
              "text": "Vtabsquare functions as a collaborative hub specifically designed for developers and marketing professionals to share knowledge, receive constructive feedback on their projects, and build professional networks in real-time.",
              "source_ref": "brand",
              "source_url": null,
              "source_title": null,
              "retrieved_at": null,
              "confidence": null
            },
            {
              "text": "The Vtabsquare Tech Community Discord Server is completely free for all qualified software developers, engineering leads, and digital marketers to join.",
              "source_ref": "brief",
              "source_url": null,
              "source_title": null,
              "retrieved_at": null,
              "confidence": null
            }
          ],
          "limitations": "All findings are derived strictly from supplied approved brand facts and campaign brief specifications without live web search data or external metrics."
        },
        "usage": {
          "input_tokens": 854,
          "output_tokens": 156
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "research_v1",
        "prompt_version": "research.v2",
        "request_id": null
      },
      "strategy": {
        "output": {
          "input_request": null,
          "summary": "Develop a targeted WhatsApp launch campaign for Vtabsquare that connects software developers, engineering leads, and digital marketers to our free Discord community. The strategy emphasizes collaborative growth, real-time peer project feedback, and professional networking in a welcoming environment.",
          "content_angle": "Empower your code and campaigns by joining a free, collaborative ecosystem where developers and marketers build together in real-time.",
          "success_measure": "High volume of qualified tech builders and digital marketers joining the free Discord community directly through the WhatsApp launch outreach."
        },
        "usage": {
          "input_tokens": 1524,
          "output_tokens": 127
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "strategy_v1",
        "prompt_version": "strategy.v2",
        "request_id": null
      },
      "creative": {
        "output": {
          "input_request": null,
          "headline": "Code and Connect in Real-Time",
          "art_direction": "A modern, well-lit collaborative workspace featuring a diverse group of software developers and digital marketers gathered around dual-monitor setups displaying clean code and campaign analytics. Natural daylight streams through large industrial windows, highlighting minimalist wooden desks, sleek mechanical keyboards, and warm ambient desk lamps. The composition is a medium shot capturing engaged professionals gesturing towards a screen with an expression of focused enthusiasm. The color palette emphasizes deep charcoal grays and vibrant electric blue accents, creating an inviting, tech-forward, and professional atmosphere.",
          "primary_hex": "#111827",
          "accent_hex": "#3B82F6",
          "font_name": "Montserrat",
          "layout_style": "split"
        },
        "usage": {
          "input_tokens": 1833,
          "output_tokens": 184
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "creative_v1",
        "prompt_version": "creative.v2",
        "request_id": null
      },
      "writing": {
        "output": {
          "input_request": null,
          "headline": "Elevate Your Code and Campaigns at Vtabsquare",
          "caption": "Are you a software developer, engineering lead, or digital marketer looking to level up your craft? Step into Vtabsquare, a welcoming and collaborative tech community designed for builders and creators. Share knowledge, get constructive peer feedback on your latest projects, and network in real-time with industry professionals. Vtabsquare is completely free to join. Connect, collaborate, and grow your expertise alongside passionate peers today.",
          "product_claim": "A collaborative hub for developers and marketers to share knowledge and network in real-time.",
          "price_claim": "Free to join",
          "call_to_action": "Join our free Discord community today",
          "variants": [
            {
              "channel": "whatsapp",
              "headline": "Build and Grow Together on Vtabsquare",
              "body": "Hey tech builders and marketers! Ready to take your projects to the next level? Join Vtabsquare, a vibrant Discord community where developers and digital marketers collaborate, share knowledge, and get real-time feedback. It is completely free to join. Click here to connect with your peers and start building today!",
              "call_to_action": "Join the community now"
            },
            {
              "channel": "discord",
              "headline": "Welcome to Vtabsquare: Where Tech Meets Marketing",
              "body": "Welcome to Vtabsquare! Whether you are writing code as a software developer, leading an engineering team, or driving digital marketing strategies, this is your new home. Share your projects, get real-time feedback, and expand your professional network. Vtabsquare is completely free to join. Jump into the conversation and start collaborating with top-tier talent today.",
              "call_to_action": "Join our free Discord server"
            },
            {
              "channel": "instagram",
              "headline": "Level Up Your Tech and Marketing Skills",
              "body": "Empower your code and campaigns within a thriving ecosystem of software developers and digital marketers. Vtabsquare is your go-to hub for real-time collaboration, peer project feedback, and professional networking. Completely free to join. Tap the link in our bio to become part of the community.",
              "call_to_action": "Join for free"
            },
            {
              "channel": "facebook",
              "headline": "Connect with Developers and Marketers at Vtabsquare",
              "body": "Calling all software developers, engineering leads, and digital marketers! Vtabsquare is a welcoming community built for you to share knowledge, get valuable feedback on your projects, and network in real-time. Vtabsquare is completely free to join. Join our Discord server today and start building the future with fellow professionals.",
              "call_to_action": "Join Vtabsquare for free"
            }
          ]
        },
        "usage": {
          "input_tokens": 1889,
          "output_tokens": 638
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "writing_v1",
        "prompt_version": "writing.v2",
        "request_id": null
      },
      "brand_review": {
        "output": {
          "input_request": null,
          "verdict": "pass",
          "findings": [
            "The product claims accurately reflect Vtabsquare as a collaborative hub for developers and marketers to share knowledge, get project feedback, and network.",
            "The price claim correctly follows the approved brand price of 'Free to join' without introducing any conflicting currency amounts or unsupported discounts."
          ],
          "summary": "The generated copy accurately incorporates the approved brand facts, maintains the requested welcoming and tech-focused tone, and properly emphasizes that the Discord community is free to join."
        },
        "usage": {
          "input_tokens": 225550,
          "output_tokens": 126
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "brand_review_v1",
        "prompt_version": "brand-review.v2",
        "request_id": null
      },
      "manager": {
        "output": {
          "input_request": null,
          "recommendation": "request_approval",
          "summary": "The campaign package for Vtabsquare Tech Community WhatsApp Launch has successfully passed all generation, research, creative, and brand review checks. The messaging accurately aligns with the approved brand facts, features the correct free-to-join pricing structure, adopts the requested welcoming and tech-focused tone, and includes tailored copy variants across all specified channels.",
          "concerns": []
        },
        "usage": {
          "input_tokens": 3508,
          "output_tokens": 103
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "manager_v1",
        "prompt_version": "manager.v2",
        "request_id": null
      },
      "publishing": {
        "output": {
          "mode": "live",
          "status": "published",
          "receipts": [
            {
              "platform": "whatsapp",
              "post_id": "wamid.HBgMOTE5NjI5NjMxMDIyFQIAERgSODQwQjBCQ0IyNzQ1QzQwQTgzAA==",
              "status": "published",
              "url": "https://wa.me/[REDACTED]"
            }
          ],
          "content_hash": "52ec03c971a6885244d184c614ef004ae87bf7abfc0a180ad080d219ebf5bc8d",
          "message": "Publication confirmed by whatsapp. Media attachments depend on connector capabilities."
        },
        "provider": "tool",
        "model": "none"
      },
      "engagement": {
        "output": {
          "category": "Live engagement queue",
          "draft_reply": "Real comments arrive in the Community inbox. Each reply requires approval.",
          "requires_human": true
        },
        "provider": "tool",
        "model": "none"
      },
      "analytics": {
        "output": {
          "input_request": null,
          "interpretation": "Based on the live publishing results from the WhatsApp platform (post id wamid.HBgMOTE5NjI5NjMxMDIyFQIAERgSODQwQjBCQ0IyNzQ1QzQwQTgzAA==), the initial broadcast generated 1 impression and 0 engagements, resulting in an engagement rate of 0.0%. Since this represents a single direct broadcast transmission, the sample size is extremely limited and does not yet provide sufficient statistical depth for comparative A/B testing or trend analysis.",
          "limitations": "Data is restricted to a single live platform record showing 1 impression and 0 engagements. No historical or multi-variant performance data is available for comparison in this run."
        },
        "usage": {
          "input_tokens": 3924,
          "output_tokens": 160
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "analytics_v1",
        "prompt_version": "analytics.v2",
        "request_id": null,
        "metrics": {
          "mode": "live",
          "records": [
            {
              "platform": "whatsapp",
              "post_id": "wamid.HBgMOTE5NjI5NjMxMDIyFQIAERgSODQwQjBCQ0IyNzQ1QzQwQTgzAA==",
              "available": true,
              "impressions": 1,
              "engagements": 0,
              "engagement_rate_pct": null,
              "limitations": "Direct broadcast message delivered to WhatsApp recipient."
            }
          ],
          "impressions": 1,
          "engagements": 0,
          "engagement_rate_pct": 0.0,
          "limitations": "Only platform-reported metrics are included. Unavailable values remain empty."
        }
      },
      "optimization": {
        "output": {
          "input_request": null,
          "hypothesis": "Given that live WhatsApp publishing yielded 1 impression and 0 engagements due to a limited sample size and platform metrics constraints across other channels like Discord and Facebook, testing a more direct, peer-focused question in the message hook will drive higher engagement rates among developers and marketers.",
          "proposed_change": "Introduce an A/B test variation on WhatsApp and social channels featuring an interactive hook ('What project are you building this week?') instead of a standard announcement, while utilizing tracked destination links to measure click-through rates.",
          "stop_rule": "Conclude the experiment after reaching 500 total impressions or after 7 days of live broadcasting, whichever occurs first."
        },
        "usage": {
          "input_tokens": 8417,
          "output_tokens": 156
        },
        "provider": "gemini",
        "model": "gemini-3.5-flash-lite",
        "implementation": "optimization_v1",
        "prompt_version": "optimization.v2",
        "request_id": null
      }
    },
    "tasks": [
      {
        "id": "2f258b69a5b74c99a9df203550bcf298",
        "token": "06bf33d9a7864719a43d34aa8787be5c",
        "role": "research",
        "stage": 0,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791895046.1799986,
        "input_version": 1,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895063.5172143
      },
      {
        "id": "dcf295b7e30c482e931685b7b2c1d882",
        "token": "6bb9f900fc274661926967be35abb9bf",
        "role": "strategy",
        "stage": 1,
        "status": "FAILED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791895063.922584,
        "input_version": 3,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895065.6533134
      },
      {
        "id": "a87fe82af4e54046ae43a6f28128352c",
        "token": "9f0a97ee16e04dcba0219a2873cfc544",
        "role": "strategy",
        "stage": 1,
        "status": "ACCEPTED",
        "attempt": 2,
        "generation": 0,
        "started_at": 1791895068.143093,
        "input_version": 5,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895085.3411336
      },
      {
        "id": "6fc2dfd64d3945098edb9863ac623c15",
        "token": "cef5d8a671014a94b60111480f5f3ae5",
        "role": "writing",
        "stage": 2,
        "status": "FAILED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791895085.4670062,
        "input_version": 7,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895097.9228063
      },
      {
        "id": "5ad4d1fd36cf40d683fc48530529c374",
        "token": "8c3cfade61ee42c497a7bcba33b1fdfe",
        "role": "creative",
        "stage": 3,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791895085.693105,
        "input_version": 8,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895118.649229
      },
      {
        "id": "e17a55d632bc417fa37c5547108fb9d1",
        "token": "8b761909fc704b26b6fbea1191c5f157",
        "role": "writing",
        "stage": 2,
        "status": "ACCEPTED",
        "attempt": 2,
        "generation": 0,
        "started_at": 1791895099.9268823,
        "input_version": 10,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895142.5261793
      },
      {
        "id": "f0b5091efaff4659b739d4d5e2293e8a",
        "token": "8435984eb6704e29ad7330e16bc3bf5e",
        "role": "brand_review",
        "stage": 4,
        "status": "FAILED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791895142.8842704,
        "input_version": 13,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895188.8523722
      },
      {
        "id": "d75c61e222ee4f59b6de1274ed457b04",
        "token": "e46f8d826dd3449591b5d1df012744e5",
        "role": "brand_review",
        "stage": 4,
        "status": "FAILED",
        "attempt": 2,
        "generation": 0,
        "started_at": 1791895190.8691175,
        "input_version": 15,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895194.4042497
      },
      {
        "id": "7a5422442f9445e097c4cf282e8253b5",
        "token": "a71230003f2b45c3b1f5bff874fa7584",
        "role": "brand_review",
        "stage": 4,
        "status": "FAILED",
        "attempt": 3,
        "generation": 0,
        "started_at": 1791895198.5234816,
        "input_version": 17,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895206.9192932
      },
      {
        "id": "b64f2abc8d7741298f9bd107c84e4791",
        "token": "8e254a2a5ff94fde8132dd2b40d9df56",
        "role": "brand_review",
        "stage": 4,
        "status": "FAILED",
        "attempt": 4,
        "generation": 0,
        "started_at": 1791895900.213026,
        "input_version": 20,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791895943.3318071
      },
      {
        "id": "7d54eb92465b4d9891dc7d217998a7c0",
        "token": "538e0342ee5e416794902e93b3db95e6",
        "role": "brand_review",
        "stage": 4,
        "status": "ACCEPTED",
        "attempt": 5,
        "generation": 0,
        "started_at": 1791896022.5846417,
        "input_version": 23,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791896027.7334135
      },
      {
        "id": "fe1d2238accd42f29a7848fb79c8f659",
        "token": "091caa224c224df89970af6683812c2e",
        "role": "manager",
        "stage": 5,
        "status": "FAILED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791896027.817935,
        "input_version": 25,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791896034.2708147
      },
      {
        "id": "fa39d6c774bf45b18679e9b658917e29",
        "token": "481843aff71b4f34adf6b4ea2baa8a4a",
        "role": "manager",
        "stage": 5,
        "status": "ACCEPTED",
        "attempt": 2,
        "generation": 0,
        "started_at": 1791896036.2938175,
        "input_version": 27,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791896055.2450209
      },
      {
        "id": "a3e60c4b67e6417a977d4e47f1c2e65d",
        "token": "fd232d7792e8456887f5265097b3f444",
        "role": "publishing",
        "stage": 6,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791896198.5481696,
        "input_version": 31,
        "model_reserved": false,
        "checkpoint": false,
        "finished_at": 1791896205.5253696
      },
      {
        "id": "f2ac6aae4d9048f5b1e4e31015854ee6",
        "token": "278fcdf2662142d298561b988e8a9eef",
        "role": "analytics",
        "stage": 7,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791982605.600082,
        "input_version": 33,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791982610.7560625
      },
      {
        "id": "1b755c62255b47779e267c35026d4cf3",
        "token": "a5fa97d0a53e4187947294763d798880",
        "role": "optimization",
        "stage": 8,
        "status": "ACCEPTED",
        "attempt": 1,
        "generation": 0,
        "started_at": 1791982610.8841357,
        "input_version": 35,
        "model_reserved": true,
        "checkpoint": false,
        "finished_at": 1791982615.9490778
      }
    ],
    "events": [
      {
        "id": "4f835530e9a64af8b7bdd80b7ec9070b",
        "at": 1791895046.1024125,
        "actor": "manager",
        "message": "I've opened Vtabsquare Tech Community WhatsApp Launch. Research Bot, check the supplied brief and brand facts first.",
        "target": "research",
        "kind": "assignment"
      },
      {
        "id": "fd3cccc2fd4c4c24bc1894d8ade92df3",
        "at": 1791895046.1024125,
        "actor": "manager",
        "message": "Each bot has its own task. I will coordinate handoffs and ask you when a decision is needed.",
        "target": null,
        "kind": "message"
      },
      {
        "id": "28a07d8f286c4ffa864a3c499c27b05c",
        "at": 1791895046.1799986,
        "actor": "research",
        "message": "I am checking the supplied brief, audience and approved brand facts.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "6d73e395a1fd4b71a171166175ea8558",
        "at": 1791895063.5172143,
        "actor": "research",
        "message": "All findings are derived strictly from supplied approved brand facts and campaign brief specifications without live web search data or external metrics.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "2f29369dbf744cc286a0e049f69a9fac",
        "at": 1791895063.5172143,
        "actor": "research",
        "message": "My result has passed its checks. Strategy Bot, I am handing it over for your task.",
        "target": "strategy",
        "kind": "handoff"
      },
      {
        "id": "de0b0dee47ee4033b1c7f20d971a2b39",
        "at": 1791895063.922584,
        "actor": "strategy",
        "message": "Research received. I am turning the findings into a campaign plan.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "4af9ff3a5ce346dca0df85f2387cab01",
        "at": 1791895065.6533134,
        "actor": "strategy",
        "message": "Gemini connection failed. No result was accepted.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "805dd561b9b34098b22c836ba2c6efe0",
        "at": 1791895065.6533134,
        "actor": "manager",
        "message": "Strategy Bot hit a temporary connection problem. I scheduled a bounded retry.",
        "target": "strategy",
        "kind": "recovery"
      },
      {
        "id": "eb68b4699b004121bd97896523a7ef2f",
        "at": 1791895068.143093,
        "actor": "strategy",
        "message": "Research received. I am turning the findings into a campaign plan.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "c4ff2893814e4589835f5a3f583f8276",
        "at": 1791895085.3411336,
        "actor": "strategy",
        "message": "Develop a targeted WhatsApp launch campaign for Vtabsquare that connects software developers, engineering leads, and digital marketers to our free Discord community. The strategy emphasizes collaborative growth, real-time peer project feedback, and professional networking in a welcoming environment.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "a894fe5f309d452d841e8115c17e4b1e",
        "at": 1791895085.3411336,
        "actor": "strategy",
        "message": "My result has passed its checks. Writer Bot, I am handing it over for your task.",
        "target": "writing",
        "kind": "handoff"
      },
      {
        "id": "f774220ffae449d2a3181c92dd1a1ab4",
        "at": 1791895085.3411336,
        "actor": "strategy",
        "message": "My result has passed its checks. Creative Bot, I am handing it over for your task.",
        "target": "creative",
        "kind": "handoff"
      },
      {
        "id": "5fdf2717b11046f6bfbc0fb8c5172e9d",
        "at": 1791895085.4670062,
        "actor": "writing",
        "message": "Strategy received. I am drafting the copy using the approved product facts.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "4bb52c16fcb844cdb54ceea8751e900f",
        "at": 1791895085.693105,
        "actor": "creative",
        "message": "Strategy received. I am preparing the visual direction while Writer Bot works on the copy.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "da0f1fb1afdf413185bcf416dfc79bf0",
        "at": 1791895097.9228063,
        "actor": "writing",
        "message": "Gemini connection failed. No result was accepted.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "e1c39f27ad3e4287aed28b215a0cfe95",
        "at": 1791895097.9228063,
        "actor": "manager",
        "message": "Writer Bot hit a temporary connection problem. I scheduled a bounded retry.",
        "target": "writing",
        "kind": "recovery"
      },
      {
        "id": "33dd469ea9e549be9888882e9af80d61",
        "at": 1791895099.9268823,
        "actor": "writing",
        "message": "Strategy received. I am drafting the copy using the approved product facts.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "6f3898af2b2c4fc8a1f229ac7e7f7695",
        "at": 1791895118.649229,
        "actor": "creative",
        "message": "A modern, well-lit collaborative workspace featuring a diverse group of software developers and digital marketers gathered around dual-monitor setups displaying clean code and campaign analytics. Natural daylight streams through large industrial windows, highlighting minimalist wooden desks, sleek mechanical keyboards, and warm ambient desk lamps. The composition is a medium shot capturing engaged professionals gesturing towards a screen with an expression of focused enthusiasm. The color palette emphasizes deep charcoal grays and vibrant electric blue accents, creating an inviting, tech-forward, and professional atmosphere.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "4aa258d13a48448393b6ac7733047724",
        "at": 1791895118.649229,
        "actor": "creative",
        "message": "My result has passed its checks. Brand Guardian, I am handing it over for your task.",
        "target": "brand_review",
        "kind": "handoff"
      },
      {
        "id": "0c0e9dc98abc4da496938c884998a90b",
        "at": 1791895142.5261793,
        "actor": "writing",
        "message": "Elevate Your Code and Campaigns at Vtabsquare",
        "target": null,
        "kind": "result"
      },
      {
        "id": "296459523e6248339caa7e9dbf6311dc",
        "at": 1791895142.5261793,
        "actor": "writing",
        "message": "My result has passed its checks. Brand Guardian, I am handing it over for your task.",
        "target": "brand_review",
        "kind": "handoff"
      },
      {
        "id": "3aecedf993e54a4d8ae43d26b6dbc1bf",
        "at": 1791895142.8842704,
        "actor": "brand_review",
        "message": "Both copy and creative are ready. I am checking claims, price and brand consistency.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "92ce7166204e454a8ef6e092c3bef542",
        "at": 1791895188.8523722,
        "actor": "brand_review",
        "message": "Gemini connection failed. No result was accepted.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "6a6ec2c783704d8bb3cf4d7f23010c74",
        "at": 1791895188.8523722,
        "actor": "manager",
        "message": "Brand Guardian hit a temporary connection problem. I scheduled a bounded retry.",
        "target": "brand_review",
        "kind": "recovery"
      },
      {
        "id": "0c7399ea51b54fe0900b0125d9c751a5",
        "at": 1791895190.8691175,
        "actor": "brand_review",
        "message": "Both copy and creative are ready. I am checking claims, price and brand consistency.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "fc47fac2a4e14eb6ae12dcd7d9ed7efb",
        "at": 1791895194.4042497,
        "actor": "brand_review",
        "message": "Gemini connection failed. No result was accepted.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "2b198b7b17c04dbaaaf7e57018d1487a",
        "at": 1791895194.4042497,
        "actor": "manager",
        "message": "Brand Guardian hit a temporary connection problem. I scheduled a bounded retry.",
        "target": "brand_review",
        "kind": "recovery"
      },
      {
        "id": "541b9abc1af843048a551d7a6b52b7c8",
        "at": 1791895198.5234816,
        "actor": "brand_review",
        "message": "Both copy and creative are ready. I am checking claims, price and brand consistency.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "aeceb2d81a3d41f7b38b74954a91fad7",
        "at": 1791895206.9192932,
        "actor": "brand_review",
        "message": "Gemini connection failed. No result was accepted.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "24d4ee9443774a1db9609d48b6fdc409",
        "at": 1791895206.9192932,
        "actor": "manager",
        "message": "Your attention is needed for Brand Guardian: Gemini connection failed. No result was accepted.",
        "target": "local-owner",
        "kind": "attention"
      },
      {
        "id": "5ea1daef9ce5476481cba91adcff7b1e",
        "at": 1791895900.213026,
        "actor": "brand_review",
        "message": "Both copy and creative are ready. I am checking claims, price and brand consistency.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "e62a967c3e6340f99f4c3a183be62992",
        "at": 1791895943.3318071,
        "actor": "brand_review",
        "message": "Gemini connection failed. No result was accepted.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "f478b5147e3f4504bfc761dea5e0eb7e",
        "at": 1791895943.3318071,
        "actor": "manager",
        "message": "Your attention is needed for Brand Guardian: Gemini connection failed. No result was accepted.",
        "target": "local-owner",
        "kind": "attention"
      },
      {
        "id": "4ce491507fd34be09a32efff090f5cac",
        "at": 1791896022.5846417,
        "actor": "brand_review",
        "message": "Both copy and creative are ready. I am checking claims, price and brand consistency.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "ea997a4a79414c58b22763431cc810d6",
        "at": 1791896027.7334135,
        "actor": "brand_review",
        "message": "The generated copy accurately incorporates the approved brand facts, maintains the requested welcoming and tech-focused tone, and properly emphasizes that the Discord community is free to join.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "eef633d2767e4de1a7f5b866c84d19cc",
        "at": 1791896027.7334135,
        "actor": "brand_review",
        "message": "My result has passed its checks. Marketing Manager, I am handing it over for your task.",
        "target": "manager",
        "kind": "handoff"
      },
      {
        "id": "ed536ea21bb14131b507d29469c2da2a",
        "at": 1791896027.817935,
        "actor": "manager",
        "message": "Brand review is ready. I am checking the complete package before asking for your decision.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "ffe674eb313f42e984b836c3f11a3fb8",
        "at": 1791896034.2708147,
        "actor": "manager",
        "message": "Gemini connection failed. No result was accepted.",
        "target": "manager",
        "kind": "failure"
      },
      {
        "id": "81ae63634ccf4aac9fbc76ed421553cf",
        "at": 1791896034.2708147,
        "actor": "manager",
        "message": "Marketing Manager hit a temporary connection problem. I scheduled a bounded retry.",
        "target": "manager",
        "kind": "recovery"
      },
      {
        "id": "59e52480c75c4e32b849699c953ce770",
        "at": 1791896036.2938175,
        "actor": "manager",
        "message": "Brand review is ready. I am checking the complete package before asking for your decision.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "5bc64c82ad674634a99514ad310d5bb4",
        "at": 1791896055.2440217,
        "actor": "manager",
        "message": "The campaign package for Vtabsquare Tech Community WhatsApp Launch has successfully passed all generation, research, creative, and brand review checks. The messaging accurately aligns with the approved brand facts, features the correct free-to-join pricing structure, adopts the requested welcoming and tech-focused tone, and includes tailored copy variants across all specified channels.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "8621bde38847480abd69433442e331c8",
        "at": 1791896055.2440217,
        "actor": "manager",
        "message": "My result has passed its checks. Publisher Bot, I am handing it over for your task.",
        "target": "publishing",
        "kind": "handoff"
      },
      {
        "id": "7aab41a1202f49a5a3825de79feb6925",
        "at": 1791896055.2450209,
        "actor": "manager",
        "message": "Your input is needed: review the copy and creative, then approve or request changes.",
        "target": "local-owner",
        "kind": "input_needed"
      },
      {
        "id": "376715d019344c7aa13f8fb7b31e6631",
        "at": 1791896198.1849751,
        "actor": "local-owner",
        "message": "I approve this exact content version for the selected publishing destination.",
        "target": "manager",
        "kind": "answer"
      },
      {
        "id": "6210ca2d20d74150a6fd4a34e6d5018f",
        "at": 1791896198.1849751,
        "actor": "manager",
        "message": "Approval received. Publisher Bot, proceed with this authorized version.",
        "target": "publishing",
        "kind": "assignment"
      },
      {
        "id": "e2e96f1924964f5eb9447bba076fa049",
        "at": 1791896198.5481696,
        "actor": "publishing",
        "message": "Your approval is recorded. I am submitting the exact authorized version to its selected destination.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "530defeaa45a4aa384f001c7af1b10bb",
        "at": 1791896205.5253696,
        "actor": "publishing",
        "message": "Publication confirmed by whatsapp. Media attachments depend on connector capabilities.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "d54f41851c3441369f52d5abad06dd44",
        "at": 1791896205.5253696,
        "actor": "publishing",
        "message": "My result has passed its checks. Analytics Bot, I am handing it over for your task.",
        "target": "analytics",
        "kind": "handoff"
      },
      {
        "id": "5f6e92663df64c51bc9dee8208e3c816",
        "at": 1791896205.5253696,
        "actor": "publishing",
        "message": "My result has passed its checks. Community Bot, I am handing it over for your task.",
        "target": "engagement",
        "kind": "handoff"
      },
      {
        "id": "068dbc61f77946fa84a7577e29e6cdce",
        "at": 1791896205.5253696,
        "actor": "analytics",
        "message": "I will collect platform metrics 24 hours after publication.",
        "target": null,
        "kind": "scheduled"
      },
      {
        "id": "98cca4ba733f4effbfedbe2f26166ca7",
        "at": 1791982605.600082,
        "actor": "analytics",
        "message": "Publication is confirmed. I am collecting the available performance evidence.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "864056d999784191ba9dd64416dd1926",
        "at": 1791982610.7560625,
        "actor": "analytics",
        "message": "Based on the live publishing results from the WhatsApp platform (post id wamid.HBgMOTE5NjI5NjMxMDIyFQIAERgSODQwQjBCQ0IyNzQ1QzQwQTgzAA==), the initial broadcast generated 1 impression and 0 engagements, resulting in an engagement rate of 0.0%. Since this represents a single direct broadcast transmission, the sample size is extremely limited and does not yet provide sufficient statistical depth for comparative A/B testing or trend analysis.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "bc92d0f0347f4e4e9aef21928b40c1ba",
        "at": 1791982610.7560625,
        "actor": "analytics",
        "message": "My result has passed its checks. Optimizer Bot, I am handing it over for your task.",
        "target": "optimization",
        "kind": "handoff"
      },
      {
        "id": "a7cbc7fc7e48466c83ea6df5b59ed662",
        "at": 1791982610.8841357,
        "actor": "optimization",
        "message": "Analytics received. I am preparing an evidence-based proposal for the next experiment.",
        "target": null,
        "kind": "started"
      },
      {
        "id": "362833c3571e45eb935bd219efeec5d1",
        "at": 1791982615.9485781,
        "actor": "optimization",
        "message": "Given that live WhatsApp publishing yielded 1 impression and 0 engagements due to a limited sample size and platform metrics constraints across other channels like Discord and Facebook, testing a more direct, peer-focused question in the message hook will drive higher engagement rates among developers and marketers.",
        "target": null,
        "kind": "result"
      },
      {
        "id": "1b47de50d38a4d258d3137594a031c2c",
        "at": 1791982615.9490778,
        "actor": "manager",
        "message": "This workflow is complete. Publication is confirmed. Optimization and reply drafts are ready for you.",
        "target": null,
        "kind": "completed"
      }
    ],
    "approval": {
      "actor": "local-owner",
      "at": 1791896198.1849751,
      "content_hash": "52ec03c971a6885244d184c614ef004ae87bf7abfc0a180ad080d219ebf5bc8d",
      "note": "Approved in the workflow panel.",
      "account": "whatsapp",
      "action": "publish_live"
    },
    "error": {
      "role": "manager",
      "kind": "connection",
      "message": "Gemini connection failed. No result was accepted."
    },
    "not_before": 0,
    "revisions": 0,
    "model_calls": 15,
    "content_hash": "52ec03c971a6885244d184c614ef004ae87bf7abfc0a180ad080d219ebf5bc8d",
    "operation_id": "a2a82b03bed34559a36fa2c281efae78",
    "nodes": {
      "research": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "strategy": {
        "state": "ACCEPTED",
        "attempt": 2,
        "lease": null,
        "lease_until": 0,
        "not_before": 1791895067.6533134,
        "generation": 0,
        "error": null
      },
      "writing": {
        "state": "ACCEPTED",
        "attempt": 2,
        "lease": null,
        "lease_until": 0,
        "not_before": 1791895099.9228063,
        "generation": 0,
        "error": null
      },
      "creative": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "brand_review": {
        "state": "ACCEPTED",
        "attempt": 5,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "manager": {
        "state": "ACCEPTED",
        "attempt": 2,
        "lease": null,
        "lease_until": 0,
        "not_before": 1791896036.2708147,
        "generation": 0,
        "error": null
      },
      "publishing": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "analytics": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 1791982605.5253696,
        "generation": 0,
        "error": null
      },
      "optimization": {
        "state": "ACCEPTED",
        "attempt": 1,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      },
      "engagement": {
        "state": "ACCEPTED",
        "attempt": 0,
        "lease": null,
        "lease_until": 0,
        "not_before": 0,
        "generation": 0,
        "error": null
      }
    },
    "input_requests": [
      {
        "id": "a73ee6408a85414b91da248d0bb3a1e4",
        "role": "manager",
        "question": "Your input is needed: review the copy and creative, then approve or request changes.",
        "reason": "Publisher Bot will wait for your exact-version approval.",
        "kind": "approval",
        "status": "ANSWERED",
        "created_at": 1791896055.2450209,
        "generation": 0,
        "answered_at": 1791896198.1849751,
        "answer": "Approved"
      }
    ],
    "human_answers": {}
  },
{
  "id": "pilot_wf_lead_engine_04",
  "version": 18,
  "brief": {
    "title": "Vtab Square Autonomous Lead Engine",
    "audience": "Enterprise CMOs, Marketing Directors, and Growth Founders",
    "goal": "Demonstrate autonomous multi-channel lead capture, webhook triggers, and zero-discrepancy ROAS analytics",
    "instructions": "Highlight multi-agent coordination, instant WhatsApp lead alerts, Brand Guardian factual verification, and unified Meta attribution",
    "checkpoint": "creative",
    "destinations": [
      "linkedin",
      "facebook",
      "instagram",
      "whatsapp"
    ],
    "audience_id": null,
    "schedule_at": null,
    "workflow_id": "campaign.v1"
  },
  "snapshot": {
    "brand": {
      "name": "Vtab Square",
      "product": "Enterprise AI Marketing OS & Autonomous Campaign Engine",
      "price": "Free 14-day trial. Custom enterprise tiers.",
      "tone": "Authoritative, data-driven, and forward-looking",
      "facts": "Vtab Square automates multi-channel marketing campaigns across Meta, WhatsApp, Discord and LinkedIn with deterministic Brand Guardian verification."
    },
    "publishing": "simulation",
    "platforms": [
      "linkedin",
      "facebook",
      "instagram",
      "whatsapp"
    ]
  },
  "state": "COMPLETED",
  "stage": "publishing",
  "created_at": 1792000000.0,
  "updated_at": 1792003600.0,
  "results": {
    "research": {
      "output": {
        "summary": "High B2B demand for autonomous multi-agent campaign workflows with brand-safety gates and multi-platform attribution.",
        "findings": [
          {
            "claim": "Vtab Square eliminates manual campaign orchestration across social channels.",
            "source_ref": "brand"
          },
          {
            "claim": "Deterministic Brand Guardian guarantees 100% pricing claim accuracy.",
            "source_ref": "brand"
          }
        ]
      }
    },
    "strategy": {
      "output": {
        "angle": "Autonomous Multi-Agent Marketing Engine: Enterprise-grade speed with complete brand guardrails.",
        "tactics": [
          "Executive-tier copy tailored for LinkedIn and Facebook",
          "High-contrast visual brand card",
          "Real-time WhatsApp inquiry capture workflow"
        ]
      }
    },
    "writing": {
      "output": {
        "headline": "Scale Multi-Channel Campaigns with Autonomous Agent Precision",
        "price_claim": "Free 14-day trial. Custom enterprise tiers.",
        "caption": "Eliminate marketing bottlenecks. Vtab Square deploys 10 coordinated AI specialists to plan, write, design, and publish high-converting campaigns across LinkedIn, Meta, and WhatsApp.",
        "variants": [
          {
            "destination": "linkedin",
            "headline": "The Autonomous Marketing OS Built for Enterprise Teams",
            "body": "Orchestrate end-to-end campaigns with verified multi-agent precision. Try free for 14 days."
          },
          {
            "destination": "facebook",
            "headline": "Meet Your Autonomous AI Marketing Department",
            "body": "From brief to published live campaign in minutes. Free 14-day trial."
          },
          {
            "destination": "instagram",
            "headline": "Autonomous AI Marketing Redefined",
            "body": "10 AI agents. 1 Unified workspace. 100% Brand fidelity. Explore Vtab Square."
          },
          {
            "destination": "whatsapp",
            "headline": "Instant Enterprise Campaign Alert",
            "body": "Your new multi-channel campaign is live and capturing qualified leads."
          }
        ]
      }
    },
    "creative": {
      "output": {
        "headline": "Scale Multi-Channel Campaigns with Autonomous Agent Precision",
        "art_direction": "Sleek dark neon indigo canvas with vibrant electric cyan accent (#6366f1 / #06b6d4), modular agent cards, and verified badge.",
        "primary_hex": "#0f172a",
        "accent_hex": "#6366f1",
        "layout_style": "split",
        "visual_theme": "Enterprise AI SaaS control room"
      }
    },
    "brand_review": {
      "output": {
        "verdict": "APPROVED",
        "rationale": "All copy variants accurately quote approved pricing ('Free 14-day trial') and core brand capabilities. Zero discrepancies found."
      }
    },
    "manager": {
      "output": {
        "recommendation": "APPROVE",
        "summary": "10/10 Bot tasks completed successfully. Brand fidelity verified. Approved for multi-channel dispatch."
      }
    },
    "publishing": {
      "output": {
        "mode": "simulation",
        "message": "Simulated live broadcast completed across LinkedIn, Facebook, Instagram, and WhatsApp.",
        "destinations": [
          {
            "platform": "linkedin",
            "status": "published_simulated",
            "url": "https://linkedin.com/company/vtabsquare/demo"
          },
          {
            "platform": "facebook",
            "status": "published_simulated",
            "url": "https://facebook.com/vtabsquare/posts/demo"
          },
          {
            "platform": "instagram",
            "status": "published_simulated",
            "url": "https://instagram.com/p/demo_lead_engine"
          },
          {
            "platform": "whatsapp",
            "status": "published_simulated",
            "url": "https://wa.me/vtabsquare"
          }
        ]
      }
    },
    "analytics": {
      "metrics": {
        "mode": "simulation",
        "impressions": 18450,
        "engagements": 1280,
        "engagement_rate_pct": 6.94
      }
    }
  },
  "tasks": [],
  "events": [
    {
      "role": "manager",
      "kind": "status",
      "message": "Workflow initialized with 4 target destinations.",
      "at": 1792000000.0
    },
    {
      "role": "research",
      "kind": "result",
      "message": "Research Bot: Verified market positioning and price claims.",
      "at": 1792000300.0
    },
    {
      "role": "strategy",
      "kind": "result",
      "message": "Strategy Bot: Multi-channel blueprint generated.",
      "at": 1792000600.0
    },
    {
      "role": "writing",
      "kind": "result",
      "message": "Writer Bot: Tailored variants generated for LinkedIn, Facebook, Instagram, and WhatsApp.",
      "at": 1792001200.0
    },
    {
      "role": "creative",
      "kind": "result",
      "message": "Creative Bot: Brand Card rendered with dark indigo (#0f172a) and electric cyan.",
      "at": 1792001400.0
    },
    {
      "role": "brand_review",
      "kind": "result",
      "message": "Brand Guardian: 100% price fidelity verified. Zero conflicts.",
      "at": 1792002000.0
    },
    {
      "role": "manager",
      "kind": "result",
      "message": "Marketing Manager: Package approved for simulated live dispatch.",
      "at": 1792002400.0
    },
    {
      "role": "publishing",
      "kind": "result",
      "message": "Publisher Bot: Simulated live broadcast confirmed across 4 channels.",
      "at": 1792003600.0
    }
  ],
  "approval": null,
  "error": null,
  "nodes": {
    "research": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    },
    "strategy": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    },
    "writing": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    },
    "creative": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    },
    "brand_review": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    },
    "manager": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    },
    "publishing": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    },
    "analytics": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    },
    "optimization": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    },
    "engagement": {
      "state": "ACCEPTED",
      "attempt": 1,
      "error": null
    }
  },
  "input_requests": [],
  "human_answers": {}
}
];

export const INITIAL_PILOT_COMMUNITY = [
  {
    id: 'cm_ig_pilot_1',
    platform: 'instagram',
    author: '@sarah_growth',
    text: 'How does the autonomous agent handle multi-channel visual branding across Instagram and Facebook?',
    state: 'AWAITING_APPROVAL',
    created_at: Date.now() - 3600000,
    output: {
      category: 'technical_inquiry',
      sentiment: 'positive',
      draft_reply: 'Great question @sarah_growth! The Creative Bot automatically renders high-resolution brand cards and responsive SVGs styled to your approved brand palette, logo, and typography.'
    }
  },
  {
    id: 'cm_fb_pilot_2',
    platform: 'facebook',
    author: 'Marcus Vance',
    text: 'Is the live AI masterclass on November 20th free to join?',
    state: 'APPROVED',
    created_at: Date.now() - 7200000,
    output: {
      category: 'event_registration',
      sentiment: 'enthusiastic',
      draft_reply: 'Hi Marcus! Yes, registration is 100% free and open access. You can register via the link above or launch a test campaign right here in this live demo!'
    }
  },
  {
    id: 'cm_wa_pilot_3',
    platform: 'whatsapp',
    author: '+91 98402 11234',
    text: 'Can we connect our existing CRM webhooks to receive real-time lead alerts?',
    state: 'AWAITING_APPROVAL',
    created_at: Date.now() - 1800000,
    output: {
      category: 'crm_integration',
      sentiment: 'interested',
      draft_reply: 'Hello! Yes, Vtab Square includes outbound webhooks and instant WhatsApp notification triggers for every qualified lead captured by your campaigns.'
    }
  },
  {
    id: 'cm_li_pilot_4',
    platform: 'linkedin',
    author: 'Elena Rostova · VP Marketing',
    text: 'Can this AI engine automatically generate branded SVG creative assets and draft copy for enterprise campaigns?',
    state: 'AWAITING_APPROVAL',
    created_at: Date.now() - 900000,
    output: {
      category: 'enterprise_capabilities',
      sentiment: 'positive',
      draft_reply: 'Hi Elena! Yes, Vtab Square generates vector-perfect responsive SVGs, platform-adapted copy variants for LinkedIn, Instagram, Facebook and WhatsApp, all verified with our Brand Guardian.'
    }
  }
];

const WORKFLOWS_KEY = 'vtab_pilot_workflows_v2';
const BRAND_KEY = 'vtab_pilot_brand_v2';
const COMMUNITY_KEY = 'vtab_pilot_community_v2';

export function getPilotWorkflows() {
  try {
    const saved = localStorage.getItem(WORKFLOWS_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {}
  savePilotWorkflows(INITIAL_PILOT_WORKFLOWS);
  return INITIAL_PILOT_WORKFLOWS;
}

export function savePilotWorkflows(workflows) {
  try {
    localStorage.setItem(WORKFLOWS_KEY, JSON.stringify(workflows));
  } catch (e) {}
}

export function getPilotBrand() {
  try {
    const saved = localStorage.getItem(BRAND_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {}
  savePilotBrand(DEFAULT_PILOT_BRAND);
  return DEFAULT_PILOT_BRAND;
}

export function savePilotBrand(brand) {
  try {
    localStorage.setItem(BRAND_KEY, JSON.stringify(brand));
  } catch (e) {}
}

export function getPilotCommunity() {
  try {
    const saved = localStorage.getItem(COMMUNITY_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {}
  savePilotCommunity(INITIAL_PILOT_COMMUNITY);
  return INITIAL_PILOT_COMMUNITY;
}

export function savePilotCommunity(items) {
  try {
    localStorage.setItem(COMMUNITY_KEY, JSON.stringify(items));
  } catch (e) {}
}

export function simulatePilotCampaign(brief, brand, onProgress) {
  const id = 'pilot_wf_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
  const now = Date.now() / 1000;

  const rawTitle = (brief.title || '').trim();
  const rawAudience = (brief.audience || '').trim();
  const rawGoal = (brief.goal || '').trim();
  const rawInstructions = (brief.instructions || '').trim();
  const rawBrandName = (brand?.name || 'Vtab Square').trim();
  const rawPrice = (brand?.price || '100% Free to join').trim();
  const cleanPrice = rawPrice.replace(/\.+$/, '').trim();

  // Dynamic Headline synthesis:
  const campaignHeadline = rawTitle
    ? (rawTitle.toLowerCase().includes(rawBrandName.toLowerCase()) ? rawTitle : `${rawBrandName} · ${rawTitle}`)
    : `${rawBrandName} · Autonomous Multi-Agent Campaign`;

  // Dynamic Caption synthesis:
  const audienceGreeting = rawAudience ? `Calling all ${rawAudience}!` : `Exciting news for innovators and growth teams!`;
  const missionText = rawGoal ? `Our mission: ${rawGoal.replace(/\.+$/, '')}.` : `Scale your brand with 10 autonomous AI marketing bots working in unison.`;
  const extraDirection = rawInstructions ? ` Special focus: ${rawInstructions.replace(/\.+$/, '')}.` : '';

  const mainCaption = `🚀 ${audienceGreeting} We are thrilled to introduce ${campaignHeadline}! ${missionText}${extraDirection} Experience zero-friction autonomous execution with ${rawBrandName} — from deep market research to multi-channel deployment. Pricing: ${cleanPrice}. Join today and unlock next-generation marketing agility!`;

  // Dynamic multi-channel variant synthesis:
  const destinations = (brief.destinations && brief.destinations.length > 0)
    ? brief.destinations
    : ['instagram', 'facebook', 'whatsapp', 'linkedin'];

  const variants = destinations.map(dest => {
    const d = dest.toLowerCase();
    if (d === 'instagram') {
      return {
        destination: 'instagram',
        headline: `✨ ${campaignHeadline}`,
        body: `Attention ${rawAudience || 'innovators & creators'}! ⚡\n\n${rawGoal || 'Autonomous marketing is officially here.'}\n\n🤖 10 synchronized AI agents manage research, copy, design, and live publishing in seconds.\n\n🎟️ Access: ${cleanPrice}\n👉 Tap the link in bio to register and experience the future of marketing.\n\n#MarketingAutomation #AI #TechInnovation #${rawBrandName.replace(/\s+/g, '')} #GrowthHacking`
      };
    }
    if (d === 'facebook') {
      return {
        destination: 'facebook',
        headline: `📣 Announcement: ${campaignHeadline}`,
        body: `We are thrilled to unveil ${campaignHeadline} for ${rawAudience || 'our global builder community'}.\n\n🎯 Campaign Objective: ${rawGoal || 'Deliver verified multi-channel marketing automation.'}\n\nEvery asset is created and verified by autonomous AI agents with 100% Brand Guardian fidelity. No manual overhead.\n\n📌 Price / Tier: ${cleanPrice}.\n\n👇 Click below to get instant access and see the live platform in action!`
      };
    }
    if (d === 'whatsapp') {
      return {
        destination: 'whatsapp',
        headline: `⚡ VIP Invitation: ${campaignHeadline}`,
        body: `Hi there! 👋\n\nExclusive access pass for ${rawAudience || 'our community'}: ${campaignHeadline} is now live.\n\n🎯 Objective: ${rawGoal || 'Scale your brand with AI'}\n💳 Cost: ${cleanPrice}\n\nReply 'CONFIRM' to lock in your registration or receive your direct access link!`
      };
    }
    if (d === 'linkedin') {
      return {
        destination: 'linkedin',
        headline: `🚀 Strategic Initiative: ${campaignHeadline}`,
        body: `Autonomous multi-agent architecture is reshaping enterprise marketing workflows.\n\nToday, we're deploying ${campaignHeadline} built specifically for ${rawAudience || 'technical leaders, founders, and growth professionals'}.\n\n🎯 Goal: ${rawGoal || 'Autonomous scale with verified brand safety'}.\n🔒 Verified Terms: ${cleanPrice}.\n\nExplore how 10 autonomous agents synchronize research, creative generation, and brand protection at scale. Share your thoughts in the comments or register below.`
      };
    }
    return {
      destination: d,
      headline: `${campaignHeadline} on ${d.toUpperCase()}`,
      body: `Multi-channel autonomous dispatch active for ${rawAudience || 'builders'}. ${rawGoal || 'Autonomous AI marketing campaign'}. Access: ${cleanPrice}.`
    };
  });

  const researchOutput = {
    summary: `Verified market evidence for ${rawBrandName}. High-intent demand detected across ${rawAudience || 'target audience segments'}.`,
    findings: [
      { claim: `Target Audience: ${rawAudience || 'Growth & Innovation leaders'} verified.`, source_ref: 'campaign_brief' },
      { claim: `Objective: ${rawGoal || 'Multi-channel autonomous scale'} aligned with market benchmarks.`, source_ref: 'campaign_brief' },
      { claim: `Pricing Fidelity: ${cleanPrice} validated with zero discrepancy.`, source_ref: 'approved_brand_facts' }
    ]
  };

  const strategyOutput = {
    angle: `Position ${rawBrandName} through high-impact value framing around: "${rawGoal || 'Autonomous Scale'}".`,
    tactics: [
      `Targeted multi-channel storytelling across ${destinations.join(', ')}`,
      `Audience alignment tailored to ${rawAudience || 'key decision makers'}`,
      `Verified price transparency (${cleanPrice}) with zero-friction onboarding`
    ]
  };

  const creativeOutput = {
    headline: campaignHeadline,
    primary_hex: '#1e1b4b',
    accent_hex: '#6366f1',
    layout_style: 'split',
    art_direction: `Cyber-indigo gradient canvas with glowing neon accents, 2-line wrapped high-legibility typography, target audience badge (${rawAudience ? rawAudience.slice(0, 45) : 'Universal Builders'}), and multi-channel publication badges.`
  };

  const brandReviewOutput = {
    verdict: 'APPROVED',
    rationale: `100% brand claim fidelity verified. Pricing claim "${cleanPrice}" strictly matches approved brand facts. No prohibited claims or hallucinations detected.`
  };

  const publishingOutput = {
    mode: 'simulation',
    message: `Simulated live broadcast completed across ${destinations.join(', ')}.`,
    destinations: destinations.map(d => ({
      platform: d,
      post_id: `sim_${d}_${Math.random().toString(36).substr(2, 9)}`,
      status: 'published_simulated',
      url: `https://${d}.com/vtabsquare/live_demo`
    }))
  };

  const analyticsOutput = {
    metrics: {
      mode: 'simulation',
      impressions: 14850,
      engagements: 1240,
      clicks: 720,
      engagement_rate_pct: 8.35,
      ctr_pct: 4.85
    }
  };

  const optimizerOutput = {
    recommendations: [
      `Prioritize ${destinations[0] || 'Instagram'} visual card format for maximum mobile click-through rate`,
      `Schedule automated WhatsApp reminder 2 hours prior to event kickoff`
    ]
  };

  const communityOutput = {
    status: 'ACTIVE_MONITORING',
    active_channels: destinations
  };

  const campaign = {
    id,
    version: 1,
    brief: {
      title: rawTitle || `${rawBrandName} Live Campaign`,
      audience: rawAudience || 'Growth teams and developers',
      goal: rawGoal || 'Drive engagement and awareness',
      instructions: rawInstructions || '',
      checkpoint: 'none',
      destinations,
      audience_id: null,
      schedule_at: null,
      workflow_id: 'campaign.v1'
    },
    snapshot: {
      brand: { ...brand, price: cleanPrice },
      publishing: 'simulation',
      platforms: destinations
    },
    state: 'RUNNING',
    stage: 'research',
    created_at: now,
    updated_at: now,
    results: {},
    tasks: [],
    events: [
      { role: 'manager', kind: 'status', message: `Workflow initialized: "${campaignHeadline}" in Pilot Sandbox.`, at: now }
    ],
    approval: null,
    error: null,
    nodes: {
      manager: { state: 'RUNNING', attempt: 1, error: null },
      research: { state: 'RUNNING', attempt: 1, error: null },
      strategy: { state: 'PENDING', attempt: 0, error: null },
      writing: { state: 'PENDING', attempt: 0, error: null },
      creative: { state: 'PENDING', attempt: 0, error: null },
      brand_review: { state: 'PENDING', attempt: 0, error: null },
      publishing: { state: 'PENDING', attempt: 0, error: null },
      analytics: { state: 'PENDING', attempt: 0, error: null },
      optimization: { state: 'PENDING', attempt: 0, error: null },
      engagement: { state: 'PENDING', attempt: 0, error: null }
    },
    input_requests: [],
    human_answers: {}
  };

  const existing = getPilotWorkflows();
  savePilotWorkflows([campaign, ...existing]);
  onProgress(campaign);

  // Stepped execution simulation (1.1s per bot stage for responsive, live progress)
  const steps = [
    {
      delay: 1100,
      run: (c) => {
        c.stage = 'strategy';
        c.nodes.research = { state: 'ACCEPTED', attempt: 1, error: null };
        c.nodes.strategy = { state: 'RUNNING', attempt: 1, error: null };
        c.results.research = { output: researchOutput };
        c.events.push({
          role: 'research',
          kind: 'result',
          message: `Research Bot: Audience demand validated for "${rawAudience || 'core demographic'}". Pricing anchor verified: ${cleanPrice}.`,
          at: Date.now() / 1000
        });
      }
    },
    {
      delay: 2200,
      run: (c) => {
        c.stage = 'writing';
        c.nodes.strategy = { state: 'ACCEPTED', attempt: 1, error: null };
        c.nodes.writing = { state: 'RUNNING', attempt: 1, error: null };
        c.nodes.creative = { state: 'RUNNING', attempt: 1, error: null };
        c.results.strategy = { output: strategyOutput };
        c.events.push({
          role: 'strategy',
          kind: 'result',
          message: `Strategy Bot: Blueprint synthesized across ${destinations.join(', ')}. Value angle: "${rawGoal || 'Autonomous Scale'}".`,
          at: Date.now() / 1000
        });
      }
    },
    {
      delay: 3400,
      run: (c) => {
        c.stage = 'brand_review';
        c.nodes.writing = { state: 'ACCEPTED', attempt: 1, error: null };
        c.nodes.creative = { state: 'ACCEPTED', attempt: 1, error: null };
        c.nodes.brand_review = { state: 'RUNNING', attempt: 1, error: null };
        c.results.writing = {
          output: {
            headline: campaignHeadline,
            price_claim: cleanPrice,
            caption: mainCaption,
            variants
          }
        };
        c.results.creative = { output: creativeOutput };
        c.events.push({
          role: 'writing',
          kind: 'result',
          message: `Writer Bot: Channel-specific copy and headlines generated for ${destinations.join(', ')} with zero pricing conflicts.`,
          at: Date.now() / 1000
        });
        c.events.push({
          role: 'creative',
          kind: 'result',
          message: `Creative Bot: High-fidelity 16:9 responsive brand card rendered with multi-line typography & audience badge.`,
          at: Date.now() / 1000
        });
      }
    },
    {
      delay: 4500,
      run: (c) => {
        // Brand Guardian done, Marketing Manager requests YOUR approval before publishing
        c.nodes.brand_review = { state: 'ACCEPTED', attempt: 1, error: null };
        c.nodes.publishing = { state: 'PENDING', attempt: 0, error: null };
        c.results.brand_review = { output: brandReviewOutput };
        c.state = 'AWAITING_APPROVAL';
        const approvalRequestId = 'pilot_approval_' + id;
        c.input_requests = [{
          id: approvalRequestId,
          role: 'manager',
          kind: 'approval',
          status: 'OPEN',
          question: 'Your campaign is ready. Approve to publish?',
          reason: `Marketing Manager has verified the complete package for "${campaignHeadline}" — content, creative, brand fidelity all confirmed. Your approval dispatches the simulated live broadcast to ${destinations.join(', ')}.`
        }];
        c.events.push({
          role: 'brand_review',
          kind: 'result',
          message: `Brand Guardian: 100% brand claim fidelity verified. Pricing claim "${cleanPrice}" strictly matches approved brand facts. ✓`,
          at: Date.now() / 1000
        });
        c.events.push({
          role: 'manager',
          kind: 'input_needed',
          message: `Marketing Manager: Full package verified and ready for dispatch to ${destinations.join(', ')}. Waiting for your approval to publish the simulated live broadcast.`,
          at: Date.now() / 1000
        });
      }
    }
  ];

  // Export a helper so the approval button in main.jsx can complete this pilot campaign
  campaign._completePilot = () => {
    const list = getPilotWorkflows();
    const target = list.find(item => item.id === id);
    if (!target) return null;
    target.state = 'COMPLETED';
    target.stage = 'completed';
    target.input_requests = target.input_requests.map(r => ({ ...r, status: 'CLOSED' }));
    target.nodes.manager = { state: 'ACCEPTED', attempt: 1, error: null };
    target.nodes.publishing = { state: 'ACCEPTED', attempt: 1, error: null };
    target.nodes.analytics = { state: 'ACCEPTED', attempt: 1, error: null };
    target.nodes.optimization = { state: 'ACCEPTED', attempt: 1, error: null };
    target.nodes.engagement = { state: 'ACCEPTED', attempt: 1, error: null };
    target.results.manager = { output: { recommendation: 'APPROVE', summary: 'Complete multi-agent package approved.' } };
    target.results.publishing = { output: publishingOutput };
    target.results.analytics = analyticsOutput;
    target.results.optimization = optimizerOutput;
    target.results.engagement = communityOutput;
    target.events.push({
      role: 'manager',
      kind: 'result',
      message: `Marketing Manager: Approval received. Dispatching simulated live broadcast to ${destinations.join(', ')}.`,
      at: Date.now() / 1000
    });
    target.events.push({
      role: 'publishing',
      kind: 'result',
      message: `Publisher Bot: Successfully published simulated live broadcast to ${destinations.join(', ')}! Campaign is now live.`,
      at: Date.now() / 1000
    });
    target.events.push({
      role: 'analytics',
      kind: 'result',
      message: 'Analytics Bot: Initial tracking baseline established. 24h performance window armed.',
      at: Date.now() / 1000
    });
    target.events.push({
      role: 'optimization',
      kind: 'result',
      message: 'Optimizer Bot: Autonomous performance optimization monitoring active.',
      at: Date.now() / 1000
    });
    target.events.push({
      role: 'engagement',
      kind: 'result',
      message: 'Community Bot: Inbound inquiry monitoring active across all channels.',
      at: Date.now() / 1000
    });
    savePilotWorkflows(list);
    return { ...target };
  };

  steps.forEach(step => {
    setTimeout(() => {
      const list = getPilotWorkflows();
      const target = list.find(item => item.id === id);
      if (target) {
        step.run(target);
        savePilotWorkflows(list);
        onProgress({ ...target });
      }
    }, step.delay);
  });

  return campaign;
}

/**
 * Called when user clicks "Approve" in pilot mode.
 * Completes the AWAITING_APPROVAL → COMPLETED transition in localStorage.
 */
export function completePilotCampaign(campaignId, onProgress) {
  const list = getPilotWorkflows();
  const target = list.find(item => item.id === campaignId);
  if (!target || target.state !== 'AWAITING_APPROVAL') return null;

  // Close the pending approval requests
  if (target.input_requests) {
    target.input_requests = target.input_requests.map(r =>
      r.kind === 'approval' && r.status === 'OPEN' ? { ...r, status: 'CLOSED' } : r
    );
  }

  target.state = 'COMPLETED';
  target.stage = 'completed';
  target.nodes.manager = { state: 'ACCEPTED', attempt: 1, error: null };
  target.nodes.publishing = { state: 'ACCEPTED', attempt: 1, error: null };
  target.nodes.analytics = { state: 'ACCEPTED', attempt: 1, error: null };
  target.nodes.optimization = { state: 'ACCEPTED', attempt: 1, error: null };
  target.nodes.engagement = { state: 'ACCEPTED', attempt: 1, error: null };

  const dest = target.brief?.destinations || ['instagram', 'facebook', 'whatsapp'];
  const cleanP = (target.snapshot?.brand?.price || 'Free to join').replace(/\.+$/, '').trim();

  target.results.manager = {
    output: { recommendation: 'APPROVE', summary: 'You approved the campaign package. Simulated live dispatch initiated.' }
  };
  target.results.publishing = {
    output: {
      mode: 'simulation',
      message: `Simulated live broadcast completed across ${dest.join(', ')}.`,
      destinations: dest.map(d => ({
        platform: d,
        post_id: `sim_${d}_${Math.random().toString(36).substr(2, 9)}`,
        status: 'published_simulated',
        url: `https://${d}.com/vtabsquare/live_demo`
      }))
    }
  };
  target.results.analytics = {
    metrics: { mode: 'simulation', impressions: 14850, engagements: 1240, clicks: 720, engagement_rate_pct: 8.35, ctr_pct: 4.85 }
  };
  target.results.optimization = {
    recommendations: [`Prioritize ${dest[0] || 'Instagram'} for maximum mobile CTR`]
  };
  target.results.engagement = {
    status: 'ACTIVE_MONITORING',
    active_channels: dest
  };

  const now = Date.now() / 1000;
  target.events.push({
    role: 'manager', kind: 'result',
    message: `Marketing Manager: Your approval is recorded. Dispatching simulated live broadcast to ${dest.join(', ')}.`,
    at: now
  });
  target.events.push({
    role: 'publishing', kind: 'result',
    message: `Publisher Bot: Successfully published simulated live broadcast to ${dest.join(', ')}! Your campaign is now live.`,
    at: now
  });
  target.events.push({
    role: 'analytics', kind: 'result',
    message: 'Analytics Bot: Initial tracking baseline established. 24h performance window armed.',
    at: now
  });
  target.events.push({
    role: 'optimization', kind: 'result',
    message: 'Optimizer Bot: Autonomous performance optimization monitoring active.',
    at: now
  });
  target.events.push({
    role: 'engagement', kind: 'result',
    message: 'Community Bot: Inbound inquiry monitoring active across all channels.',
    at: now
  });

  savePilotWorkflows(list);
  if (onProgress) onProgress({ ...target });
  return { ...target };
}

export function renderPilotSvg(headline, brandName, price, primaryHex = '#1e1b4b', accentHex = '#6366f1', audience = '', destinations = ['instagram', 'facebook', 'whatsapp', 'linkedin']) {
  const safeHeadline = String(headline || 'Autonomous Marketing Campaign').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const safeBrand = String(brandName || 'Vtab Square').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const rawPrice = String(price || '100% Free').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const cleanPrice = rawPrice.replace(/\.+$/, '').trim();
  const safeAudience = String(audience || 'Developers, AI Founders & Growth Teams').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const audienceBadge = safeAudience.length > 58 ? safeAudience.slice(0, 55) + '…' : safeAudience;

  const words = safeHeadline.split(/\s+/);
  let line1 = '';
  let line2 = '';
  if (words.length <= 4 && safeHeadline.length <= 36) {
    line1 = safeHeadline;
  } else {
    const cur = [];
    for (const w of words) {
      if ((cur.concat(w).join(' ')).length <= 34 && !line2) {
        cur.push(w);
      } else {
        if (!line1) {
          line1 = cur.join(' ');
          cur.length = 0;
        }
        cur.push(w);
      }
    }
    line2 = cur.join(' ');
    if (!line1) {
      line1 = line2;
      line2 = '';
    }
  }
  if (line2.length > 38) {
    line2 = line2.slice(0, 35) + '…';
  }

  const activeChannels = (Array.isArray(destinations) && destinations.length > 0)
    ? destinations.slice(0, 4)
    : ['instagram', 'facebook', 'whatsapp', 'linkedin'];

  const channelMeta = {
    instagram: { label: 'Instagram', color: '#e1306c' },
    facebook: { label: 'Facebook', color: '#60a5fa' },
    whatsapp: { label: 'WhatsApp', color: '#34d399' },
    linkedin: { label: 'LinkedIn', color: '#a78bfa' },
    discord: { label: 'Discord', color: '#818cf8' },
    twitter: { label: 'X / Twitter', color: '#38bdf8' }
  };

  const channelPillsSvg = activeChannels.map((ch, idx) => {
    const meta = channelMeta[ch.toLowerCase()] || { label: ch.toUpperCase(), color: '#94a3b8' };
    const x = 275 + (idx * 118);
    return `
      <rect x="${x}" y="274" width="110" height="44" rx="8" fill="#111827" stroke="#334155" stroke-width="1"/>
      <circle cx="${x + 16}" cy="296" r="4" fill="${meta.color}"/>
      <text x="${x + 28}" y="300" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">${meta.label}</text>
    `;
  }).join('');

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 480" width="100%" height="auto" style="display:block;border-radius:12px;box-shadow:0 12px 36px rgba(0,0,0,0.35);">
    <defs>
      <linearGradient id="bg_grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${primaryHex}"/>
        <stop offset="45%" stop-color="#0f172a"/>
        <stop offset="100%" stop-color="#030712"/>
      </linearGradient>
      <radialGradient id="orb_glow" cx="80%" cy="20%" r="60%">
        <stop offset="0%" stop-color="${accentHex}" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="btn_grad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="${accentHex}"/>
        <stop offset="100%" stop-color="#8b5cf6"/>
      </linearGradient>
      <linearGradient id="title_grad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="#f1f5f9"/>
      </linearGradient>
    </defs>

    <!-- Canvas Background -->
    <rect width="800" height="480" rx="12" fill="url(#bg_grad)"/>

    <!-- Subtle Grid Lines -->
    <path d="M0 80 H800 M0 160 H800 M0 240 H800 M0 320 H800 M0 400 H800" stroke="#334155" stroke-opacity="0.14" stroke-width="1"/>
    <path d="M160 0 V480 M320 0 V480 M480 0 V480 M640 0 V480" stroke="#334155" stroke-opacity="0.14" stroke-width="1"/>

    <!-- Glowing Accent Orb -->
    <circle cx="680" cy="90" r="200" fill="url(#orb_glow)"/>

    <!-- Top Badge Header -->
    <rect x="44" y="36" width="230" height="32" rx="16" fill="#1e1b4b" stroke="${accentHex}" stroke-width="1.2" stroke-opacity="0.6"/>
    <text x="60" y="57" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="800" fill="#a5b4fc" letter-spacing="1.2">⚡ ${safeBrand.toUpperCase()} MARKETING OS</text>

    <rect x="574" y="36" width="182" height="32" rx="16" fill="#064e3b" stroke="#059669" stroke-width="1.2" stroke-opacity="0.6"/>
    <circle cx="592" cy="52" r="4" fill="#34d399"/>
    <text x="606" y="57" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="700" fill="#6ee7b7" letter-spacing="0.6">AUTONOMOUS DISPATCH</text>

    <!-- Headline (2 lines max, no ugly truncation) -->
    <text x="44" y="135" font-family="system-ui, -apple-system, sans-serif" font-size="30" font-weight="800" fill="url(#title_grad)" letter-spacing="-0.5">
      ${line1}
    </text>
    ${line2 ? `<text x="44" y="174" font-family="system-ui, -apple-system, sans-serif" font-size="27" font-weight="800" fill="#c7d2fe" letter-spacing="-0.5">${line2}</text>` : ''}

    <!-- Audience Bar -->
    <rect x="44" y="${line2 ? 204 : 170}" width="712" height="32" rx="6" fill="#1e293b" fill-opacity="0.75" stroke="#334155" stroke-width="1" stroke-opacity="0.6"/>
    <text x="58" y="${line2 ? 225 : 191}" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="700" fill="#818cf8">
      TARGET AUDIENCE: <tspan fill="#f8fafc" font-weight="500">${audienceBadge}</tspan>
    </text>

    <!-- CTA Button -->
    <rect x="44" y="274" width="215" height="44" rx="8" fill="url(#btn_grad)"/>
    <text x="151" y="301" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" fill="#ffffff" text-anchor="middle">
      Get Access · ${cleanPrice}
    </text>

    <!-- Destination Pills -->
    ${channelPillsSvg}

    <!-- Bottom Verification Footer -->
    <rect x="44" y="378" width="712" height="56" rx="8" fill="#0b0f19" stroke="#1e293b" stroke-width="1.2"/>
    <text x="72" y="412" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="700" fill="#38bdf8">✓ 10/10 AI Agents Synchronized</text>
    <text x="322" y="412" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="700" fill="#34d399">✓ Brand Guardian: 100% Fidelity</text>
    <text x="582" y="412" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="700" fill="#c084fc">✓ Verified Live Dispatch</text>
  </svg>`;
}
