# LifeLink AI UI/UX audit

**Audit baseline:** 26 September 2026. Repository pages and shared frontend architecture reviewed against `README.md`, `ARCHITECTURE.md` (frontend and authentication sections), `API.md` (auth, donor, hospital, blood-bank, inventory, emergency and matching contracts), and the existing screenshot index. This is a code audit; the screenshots are historical and are not treated as proof of current routes or functionality.

## Actual frontend routes

The App Router contains 20 `page.tsx` files (one root page and 19 pages in route groups), including the two dynamic tracking/detail patterns below. Route groups do not add URL segments.

| Route | Page and actual workflow | Access / current data path | Phase 2 status |
|---|---|---|---|
| `/` | Public home, emergency entry, request tracking lookup, compatibility information | Public; links to public emergency intake/tracking | Shared header updated; page content still needs full visual review |
| `/about` | Platform information | Public | Shared header/skip link updated |
| `/login` | User sign in and role routing | Public; existing auth service/store | Shared header/skip link updated; auth flow preserved |
| `/register` | Account creation and role selection | Public; existing auth service | Shared header/skip link updated; page-level form review remains |
| `/admin/login` | Admin login and database-backed demo-account sign-in | Public; existing auth service | Shared header/skip link updated; backend authentication unchanged |
| `/emergency` | Public emergency intake and tracking-code lookup | Public; emergency service; existing fields and rules | Phase 1 three-step flow retained; shared shell updated |
| `/emergency/track/[id]` | Public status tracking | Public; emergency service; public-safe data | Shared shell updated; map effect warnings remain |
| `/dashboard` | Authenticated role router/account hub | Authenticated; existing role helper/store | Shared responsive shell updated; page content needs review |
| `/donor` | Donor onboarding/readiness, availability, emergency opportunities, profile editor | Donor; donor service | Shared responsive shell updated; donor workflow page review remains |
| `/donor/profile` | Donor account and eligibility profile | Donor; donor service | Shared responsive shell updated; form details need review |
| `/donor/opportunities/[id]` | Opportunity details and donor response | Donor; donor/matching services | Shared responsive shell updated; action workflow needs review |
| `/hospital` | Hospital overview, request creation and current requisitions | Hospital staff; hospital service | Shared responsive shell updated; table/form details need review |
| `/hospital/emergency` | Emergency operations workspace | Hospital staff; existing hospital/emergency services | Shared responsive shell updated; workflow needs review |
| `/hospital/emergency/track/[id]` | Hospital request tracking | Hospital staff; existing emergency service | Shared responsive shell updated; map effect warnings remain |
| `/hospital/requests` | Hospital requisition list and management | Hospital staff; hospital service | Shared responsive shell updated; table/filter details need review |
| `/hospital/requests/[id]/matches` | Existing matching and coordination workspace | Hospital staff; matching service | Shared responsive shell updated; detailed privacy/workflow review remains |
| `/hospital/profile` | Facility profile | Hospital staff; hospital service | Shared responsive shell updated; form details need review |
| `/blood-bank` | Blood-bank dashboard, inventory and emergency demand/response | Blood-bank staff; blood-bank services and existing API data | Shared responsive shell updated; table/modal details need review |
| `/blood-bank/profile` | Blood-bank facility profile | Blood-bank staff; blood-bank service | Shared responsive shell updated; form details need review |
| `/admin` | Facility verification/administrative overview | Administrator; admin service | Shared responsive shell updated; administrative action review remains |

No separate notification, messaging, analytics, facility staff-management, request-history, or governance route exists in the actual App Router pages. No missing page or backend feature was invented. The architecture document contains older example routes that do not match this App Router; the README says 15 pages while the actual count is 20. The screenshot index includes illustrative screens/features such as GPS picker, push/live updates and separate fulfilment/governance screens that cannot be verified in current route code.

## Findings

- The Phase 1 clinical palette and common controls were present, but the global header repeated role links already present in dashboard navigation. The mobile menu omitted some destinations, displayed emoji as navigation cues, and did not close on Escape or route changes.
- Dashboard navigation became a narrow vertical sidebar at tablet widths, limiting space for dense operational pages.
- The shared dialog did not contain keyboard focus, restore focus to its opener, or constrain long content to short mobile viewports.
- Existing dashboards and workflows remain API-backed. Tables, forms and page-specific states vary significantly; the common shell work below does not constitute a completed page-by-page redesign.
- The previous tracking pages had four `originCoord` effect dependency warnings. Both pages were replaced with one API-backed status view, which removed the warning source along with the nonfunctional simulated map.
- Demo screenshot automation attempts to select demo personas; this audit did not use it because it can submit sign-in requests and implies demo credentials are preconfigured. No operational request, donor response, availability change, stock update or facility verification was submitted.

## Phase 1 foundation retained

- Clinical light semantic tokens, dark-theme support, focus styles and reduced-motion rules in `frontend/styles/globals.css`.
- Light theme default and theme handling in the root/theme provider.
- Touch-sized shared button/input components.
- Public landing route fixes and three-step account-free emergency intake using the existing request fields and payload.

## Phase 2 changes completed in this pass

- Rebuilt `frontend/components/layout/Navbar.tsx` as a single public header with a consistent emergency action, account controls and accessible mobile menu. Role-specific links stay in the existing role-scoped dashboard sidebar.
- Updated `frontend/components/layout/Sidebar.tsx` and dashboard layout so tablet widths use full-width horizontal role navigation; the persistent desktop sidebar begins at 1024 px.
- Added skip links and keyboard-focusable main regions to public and authenticated layouts.
- Updated `frontend/components/ui/Modal.tsx` for mobile-height scrolling, 44 px close control, initial focus, Tab focus containment, Escape dismissal and opener-focus restoration.
- Replaced the fabricated GPS/dispatch animation and hospital demo fallback in both tracker pages with `frontend/components/features/emergency/RequestTrackingView.tsx`, which uses the existing request API and renders its actual status. Removed unsupported live/cold-chain claims from public copy and blood-bank workflow text.
- Added two focused modal keyboard tests and a Jest config scoped to the test directory.

## Verification status

- `npm run type-check`: passed after the modal tests were included.
- `npm run lint`: passed with no warnings after replacing the simulated tracking screens.
- `npx jest __tests__/Modal.test.tsx --runInBand --verbose`: passed, 2 tests.
- `npm run build`: passed; all 20 routes were generated or bundled.
- Browser visual checks covered the seven public routes at 320, 375, 390, 430, 768, 1024, 1440 and 1600 px (56 route/viewport combinations) with no horizontal overflow. Mobile navigation opened and closed with Escape. Authenticated role pages have not yet had a browser pass using a real database session.

## Remaining page-by-page work

The 20 routes above are mapped, but most page bodies still require their own task hierarchy, form/table/empty/error-state review and verified screenshots. Priority is emergency/hospital operations, donor readiness and blood-bank inventory, followed by profiles/authentication and admin governance. Current screenshots in `screenshots/` predate this pass and are retained as historical references, not labelled as verified Phase 2 before/after evidence.

## Phase 3 role-page review

Phase 3 changes are recorded separately in `docs/UI_UX_PHASE_3_REPORT.md`. The Docker CLI is unavailable in this environment, so no authenticated role session or live-data screenshots could be established. Findings below are code-path reviews and static checks; they do not certify actual user journeys or responsive screenshots.

| Route | Page-specific review and changes | Status |
|---|---|---|
| `/dashboard` | Existing authenticated role router and page are retained; no role-routing or authorization behavior was changed in Phase 3. | Code path not changed; live role routing unverified |
| `/donor` | Removed assumed blood type, body details and gender from first-use fields; added an explicit availability choice; API load failures no longer fall through to onboarding; eligibility uses the donor service response instead of a fixed cooldown claim; opportunity cards show the returned component and current-result language. | Code changes; build checks only; authenticated workflow and viewports unverified |
| `/donor/profile` | Failed profile loads now block editing and offer retry; removed duplicate frontend cooldown math; shows API-provided eligibility and profile donation summary; marks detailed history unavailable because no detailed history endpoint/page is present. | Code changes; build checks only; authenticated workflow and viewports unverified |
| `/donor/opportunities/[id]` | Displays the returned component and pending response accurately; added confirmation before accept/decline; errors are surfaced and retryable; removed false facility/pulse cues. | Code changes; no donor response submitted; authenticated workflow and viewports unverified |
| Donor donation history | No separate route or detailed donation-history API endpoint was found. The profile now exposes only summary fields returned by the existing profile response. | Existing functionality limit documented; not invented |
| `/hospital` | Requisition defaults no longer imply O-negative, two units or critical urgency; failed dashboard loads do not render zero metrics; unknown facility/date values are identified; removed fake tracking pulse. | Code changes; no request created; authenticated workflow and viewports unverified |
| `/hospital/emergency` | This legacy route redirects to `/hospital/requests` so hospital navigation remains in its role workspace instead of switching to public intake. | Route behavior reviewed; browser session unverified |
| `/hospital/requests` | Request list supports previous/next service pagination; page-local status filters expose pressed state; API failures have retry and do not appear as empty results; assumed requisition fields removed. | Code changes; no request created; authenticated workflow and viewports unverified |
| `/hospital/requests/[id]/matches` | Request-load and matching-result failure states are distinct from a true zero-candidate result; clarified facility fallback and removed real-time wording. Existing matching services remain unchanged. | Code changes; matching not executed; authenticated workflow and viewports unverified |
| `/hospital/profile` | Non-404 profile API failures no longer open a blank registration form; registration copy no longer promises immediate activation. | Code changes; no profile saved/deleted; authenticated workflow and viewports unverified |
| `/hospital/emergency/track/[id]` | Shared API-backed tracking from Phase 2 retained. No authenticated status request could be checked in this environment. | Phase 2 implementation retained; live authenticated status unverified |
| `/blood-bank` | Missing metrics show unavailable, not zero; inventory empty state is explicit; demand-availability failures are not left as an endless loading label; stock reservation defaults to one unit; removed unsupported “live/physically verified/no mock” claims and synthetic audit note. | Code changes; no inventory or demand mutation; authenticated workflow and viewports unverified |
| `/blood-bank/profile` | Non-404 profile failures block blank registration; removed immediate activation promise; initial walk-in setting is not preselected for a new facility. | Code changes; no profile saved/deleted; authenticated workflow and viewports unverified |
| `/admin` | Status changes require confirmation; certificate screen states it displays a reference only and does not verify/open the document; service failures remain separate from empty facility results; status counts are unavailable when not loaded. | Code changes; no administrative status changed; authenticated workflow and viewports unverified |
| Admin user management and audit history | No separate user-management, audit-log, or governance route/API workflow was found in the current frontend route inventory. `/admin` currently lists facilities and permits status changes only. | Not present; not fabricated |

### Phase 3 code-level issues identified

- The donor UI implied a cooldown duration different from the server response; the client now renders the existing API values.
- New donor and hospital requisition forms had preselected health/emergency values that could be submitted without an explicit selection; these fields now start unselected.
- Several service failures were visually indistinguishable from valid empty or zero data; affected pages now show retry/unavailable states.
- Hospital request timestamps had a fabricated “Just now” fallback; missing timestamps now display as unavailable.
- The admin certificate panel implied external registry verification without doing a verification request; it now labels the saved reference only.
- Phase 3 did not alter API contracts, database structures, or operational algorithms. No database or operational action was performed.

### Phase 3 verification results

- `npm run type-check`: passed.
- `npm run lint`: passed without warnings or errors.
- `npm test -- --runInBand`: passed; 1 suite, 2 modal keyboard tests.
- `npm run build`: passed; all 20 application routes compiled/generated.
- Docker/API-backed role workflows, responsive page screenshots, and the requested 8 viewport widths remain unverified. Phase 2's viewport checks cover public routes only.
