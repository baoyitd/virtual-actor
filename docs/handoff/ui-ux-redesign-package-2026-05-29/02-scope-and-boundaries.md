# 02. Scope And Boundaries

## Current Redesign Focus

The new partner is being asked to redesign the product UI/UE/UX at an overall level, not just to beautify a few pages.

The redesign should cover the main product surfaces:

1. login
2. global navigation and layout
3. role asset list
4. role detail
5. role create/edit
6. knowledge binding experience
7. test desk
8. usage desk
9. marketplace
10. dashboard

## Hard Product Boundaries

The redesign may challenge current page structure, flow shape, and interaction design, but it should not silently change these product-level boundaries:

1. The core product chain remains:
   `AI creation -> asset governance -> test & publish -> unified consumption -> operational evidence`
2. React is the formal user-facing UI.
3. The platform must continue to rely on real knowledge-platform integration, not mock data.
4. The product still needs to distinguish testing from formal usage.
5. Structured business output is a core concept, not optional decoration.
6. Consumption results still need explicit status and boundary signals.

## Product Concepts That Must Still Exist

The redesign should preserve these concepts at the product level, even if the UI form changes:

1. role assets
2. role versions
3. knowledge binding
4. test before publish
5. formal usage after publish
6. marketplace-style discovery
7. operational evidence / dashboard

## Current Non-Goals

The redesign does **not** need to introduce product capabilities that are outside the current scope, such as:

1. RBAC / multi-tenant SaaS system
2. A3 execution mechanism
3. role template library as a standalone product module
4. custom schema builder UI as a formal shipped capability
5. streaming output design as a required baseline

## Design Freedom

The new partner should feel free to rethink:

1. overall information architecture
2. navigation model
3. page grouping
4. page hierarchy
5. interaction patterns
6. content density
7. form guidance
8. result presentation
9. marketplace expression
10. dashboard expression

The redesign should not assume that the current page structure is already correct.
