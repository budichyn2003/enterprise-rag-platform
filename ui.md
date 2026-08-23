# 🎨 Maincore UI Design System

> **Reusable UI Standard for Fullstack, AI & Web Projects**

`ui.md` adalah standar visual yang digunakan oleh seluruh project yang dibangun menggunakan **Maincore**.

Dokumen ini menjadi **single source of truth** untuk keputusan UI agar setiap project memiliki karakter visual yang konsisten, modern, profesional, dan mudah dikembangkan.

---

# 1. 🎯 Design Philosophy

Maincore menggunakan pendekatan:

> **Modern · Clean · Glassmorphism · Professional · Responsive**

UI harus terasa:

* Modern
* Minimal
* Profesional
* Teknologi
* Ringan
* Konsisten
* Mudah digunakan
* Responsive
* Accessible

### Prinsip utama

1. **Consistency First**
2. **Reuse Before Create**
3. **Simple Over Complex**
4. **Whitespace Is Important**
5. **Visual Hierarchy Must Be Clear**
6. **Responsive By Default**
7. **Accessibility Matters**
8. **Do Not Overuse Effects**

Glassmorphism digunakan sebagai **visual language**, bukan sebagai dekorasi di setiap elemen.

---

# 2. 🎨 Color System

Maincore menggunakan palet biru sebagai identitas utama.

## Primary Palette

| Token        | Color     | Usage                         |
| ------------ | --------- | ----------------------------- |
| `mc-base`    | `#FFFFFC` | Main background               |
| `mc-soft`    | `#DFE7F7` | Soft background / muted state |
| `mc-primary` | `#234CF9` | Primary action                |
| `mc-dark`    | `#1C277B` | Heading / deep accent         |

### Color Meaning

#### `#FFFFFC` — Base

Digunakan sebagai:

* Main page background
* Surface background
* Empty state background
* Light UI surface

#### `#DFE7F7` — Soft

Digunakan sebagai:

* Secondary background
* Hover background
* Input background
* Muted section
* Disabled surface

#### `#234CF9` — Primary

Digunakan sebagai:

* Primary button
* CTA
* Active navigation
* Links
* Focus state
* Important highlights
* AI actions

#### `#1C277B` — Dark

Digunakan sebagai:

* Heading
* Strong text
* Dark glass surface
* Navigation accent
* High contrast UI

---

# 3. 🚦 Semantic Colors

Semantic colors digunakan untuk memberikan informasi mengenai status sistem.

| Token   | Color     | Usage       |
| ------- | --------- | ----------- |
| Success | `#16A34A` | Success     |
| Warning | `#F59E0B` | Warning     |
| Error   | `#EF4444` | Error       |
| Info    | `#2563EB` | Information |

Semantic colors hanya digunakan ketika memiliki **makna fungsional**.

Jangan menggunakan warna merah, hijau, atau kuning hanya sebagai dekorasi.

---

# 4. ⚙️ Tailwind Color Configuration

Jika project menggunakan Tailwind configuration:

```typescript
theme: {
  extend: {
    colors: {
      mc: {
        base: "#FFFFFC",
        soft: "#DFE7F7",
        primary: "#234CF9",
        dark: "#1C277B",
      },
    },
  },
}
```

Semantic colors:

```typescript
colors: {
  success: "#16A34A",
  warning: "#F59E0B",
  error: "#EF4444",
  info: "#2563EB",
}
```

> Jika project menggunakan Tailwind CSS versi terbaru dengan pendekatan CSS-first, gunakan CSS variables/theme tokens sebagai pengganti `tailwind.config.ts`.

---

# 5. 🔤 Typography

Font utama Maincore:

> **Jakarta Sans**

Jakarta Sans digunakan karena memiliki karakter:

* Modern
* Clean
* Professional
* Highly readable
* Cocok untuk dashboard
* Cocok untuk AI application
* Cocok untuk SaaS

## Font Family

```css
font-family: "Plus Jakarta Sans", sans-serif;
```

Recommended Google Font:

```text
Plus Jakarta Sans
```

Jika project menggunakan Next.js:

```typescript
import { Plus_Jakarta_Sans } from "next/font/google";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
});
```

Gunakan variable tersebut sebagai font utama aplikasi.

---

# 6. 📐 Typography Scale

| Element    | Size | Weight |
| ---------- | ---: | -----: |
| Display    | 48px |    700 |
| H1         | 36px |    700 |
| H2         | 30px |    700 |
| H3         | 24px |    600 |
| H4         | 20px |    600 |
| Body Large | 18px |    400 |
| Body       | 16px |    400 |
| Body Small | 14px |    400 |
| Caption    | 12px |    400 |

### Heading Rules

Heading harus:

* Singkat
* Jelas
* Memiliki hierarchy
* Tidak menggunakan terlalu banyak weight
* Tidak menggunakan gradient text secara berlebihan

Recommended:

```text
H1 → 36px / Bold
H2 → 30px / Bold
H3 → 24px / SemiBold
H4 → 20px / SemiBold
```

---

# 7. 🪞 Glassmorphism System

Glassmorphism adalah visual style utama Maincore.

Namun efek glass harus digunakan secara terkontrol.

## Glass Principles

Glass component memiliki:

```text
Transparency
+
Backdrop Blur
+
Subtle Border
+
Soft Shadow
```

Jangan menggunakan:

* Blur berlebihan
* Opacity terlalu rendah
* Border terlalu terang
* Shadow terlalu kuat
* Glass pada semua element

---

# 8. 🧊 Glass Components

## Standard Glass Panel

```css
@layer utilities {
  .glass-panel {
    @apply bg-white/40 backdrop-blur-md border border-white/50 shadow-sm;
  }
}
```

## Dark Glass

```css
@layer utilities {
  .glass-panel-dark {
    @apply bg-mc-dark/10 backdrop-blur-lg border border-mc-dark/20;
  }
}
```

## Strong Glass

```css
@layer utilities {
  .glass-panel-strong {
    @apply bg-white/60 backdrop-blur-xl border border-white/60 shadow-md;
  }
}
```

### Usage

```tsx
<div className="glass-panel rounded-xl p-6">
  Content
</div>
```

---

# 9. 🔲 Border Radius

Maincore menggunakan radius yang modern tetapi tetap profesional.

### Standard

```text
rounded-lg  → 8px
rounded-xl  → 12px
```

### Rules

Gunakan:

```text
rounded-lg
rounded-xl
```

Untuk:

* Card
* Button
* Input
* Modal
* Navigation
* Container

Hindari:

```text
rounded-2xl
rounded-3xl
```

pada container utama kecuali memang dibutuhkan oleh desain.

`rounded-full` hanya digunakan untuk:

* Avatar
* Badge tertentu
* Icon button tertentu
* Status indicator

---

# 10. 🔘 Buttons

Button harus memiliki:

* Clear hierarchy
* Strong contrast
* Smooth interaction
* Accessible text
* Consistent sizing

## Primary

```tsx
className="
bg-mc-primary
text-white
rounded-lg
px-4
py-2
hover:bg-mc-dark
transition-colors
duration-200
"
```

## Secondary

```tsx
className="
bg-mc-soft
text-mc-dark
rounded-lg
px-4
py-2
hover:bg-white
transition-colors
duration-200
"
```

## Glass Button

```tsx
className="
glass-panel
text-mc-dark
rounded-lg
px-4
py-2
hover:bg-white/60
transition-colors
duration-200
"
```

## Outline

```tsx
className="
border
border-mc-primary
text-mc-primary
rounded-lg
px-4
py-2
hover:bg-mc-primary
hover:text-white
transition-colors
duration-200
"
```

## Danger

```tsx
className="
bg-red-500
text-white
rounded-lg
px-4
py-2
hover:bg-red-600
transition-colors
duration-200
"
```

### Button Sizes

```text
sm → px-3 py-1.5
md → px-4 py-2
lg → px-6 py-3
```

---

# 11. 📝 Form & Input

Input harus terlihat clean dan tidak terlalu dekoratif.

## Standard Input

```tsx
className="
w-full
rounded-lg
border
border-mc-soft
bg-white/60
px-4
py-2.5
text-mc-dark
outline-none
transition
focus:border-mc-primary
focus:ring-2
focus:ring-mc-primary/20
"
```

### Input States

Input harus memiliki state:

```text
Default
Hover
Focus
Filled
Disabled
Error
Success
```

### Error

```text
Border → error
Text → error
Helper text → error
```

Jangan hanya menggunakan warna untuk menunjukkan error.

---

# 12. 🃏 Cards

Card merupakan salah satu komponen utama Maincore.

## Standard Card

```tsx
<div className="glass-panel rounded-xl p-6">
  ...
</div>
```

Card harus memiliki:

```text
Padding
+
Hierarchy
+
Clear Content
```

Recommended:

```text
p-4
p-5
p-6
```

Hindari card yang terlalu padat.

---

# 13. ✨ Interactive Card

Card yang dapat diklik boleh menggunakan hover effect.

```tsx
className="
glass-panel
rounded-xl
p-6
transition
duration-200
hover:-translate-y-0.5
hover:shadow-md
"
```

Animation harus subtle.

Hindari:

```text
bounce
large scale
excessive rotation
```

---

# 14. 🧭 Navigation

Navigation harus memiliki hierarchy yang jelas.

## Sidebar

Sidebar dapat menggunakan:

```text
glass-panel-dark
```

atau surface solid.

### Active Item

Active navigation menggunakan:

```text
mc-primary
```

dengan contrast yang jelas.

Example:

```tsx
className="
bg-mc-primary
text-white
rounded-lg
px-3
py-2
"
```

### Navigation Rules

* Icon harus konsisten
* Label harus singkat
* Active state harus jelas
* Jangan menggunakan terlalu banyak warna
* Mobile harus memiliki navigation alternative

---

# 15. 📱 Responsive Design

Semua Maincore project harus responsive.

Minimal breakpoint:

```text
Mobile
Tablet
Desktop
Large Desktop
```

Recommended Tailwind approach:

```text
mobile-first
sm:
md:
lg:
xl:
```

Contoh:

```tsx
<div className="
grid
grid-cols-1
md:grid-cols-2
lg:grid-cols-3
gap-6
">
```

### Mobile Rules

Pada mobile:

* Sidebar menjadi drawer
* Navigation menjadi compact
* Card menjadi full width
* Table dapat menjadi horizontal scroll
* Font tetap readable
* Button tidak terlalu kecil

---

# 16. 📏 Spacing System

Gunakan spacing Tailwind secara konsisten.

Recommended:

```text
gap-2
gap-3
gap-4
gap-6
gap-8
```

### General Rules

```text
2 → tight
4 → standard
6 → comfortable
8 → section
12+ → major separation
```

Hindari spacing random seperti:

```text
17px
23px
31px
37px
```

kecuali memang dibutuhkan oleh desain khusus.

---

# 17. 🧱 Page Layout

Page harus memiliki struktur visual yang jelas.

Recommended:

```text
Page
│
├── Header
│
├── Page Introduction
│   ├── Title
│   └── Description
│
├── Main Content
│
└── Supporting Content
```

Dashboard:

```text
Dashboard
│
├── Header
│
├── Overview
│   ├── Statistic
│   ├── Statistic
│   └── Statistic
│
├── Main Content
│
└── Secondary Content
```

---

# 18. 📊 Tables

Table digunakan untuk data terstruktur.

Table harus:

* Readable
* Compact
* Responsive
* Memiliki clear header
* Memiliki hover state

Header:

```text
bg-mc-soft
text-mc-dark
font-semibold
```

Row:

```text
border-b
hover:bg-mc-soft/50
```

Untuk mobile:

```text
overflow-x-auto
```

Jangan membuat table terlalu dekoratif.

Data adalah prioritas utama.

---

# 19. 🏷️ Badges

Badge digunakan untuk:

* Status
* Category
* Role
* Label

Contoh:

```tsx
<span className="
rounded-full
bg-mc-soft
px-2.5
py-1
text-xs
font-medium
text-mc-dark
">
  Active
</span>
```

Gunakan `rounded-full` untuk badge diperbolehkan.

---

# 20. 🚨 Alerts

Alert harus menggunakan semantic color.

### Success

```text
Green
```

### Warning

```text
Yellow / Orange
```

### Error

```text
Red
```

### Info

```text
Blue
```

Alert harus memiliki:

```text
Icon
+
Title
+
Description
```

Jika diperlukan:

```text
Close Action
```

---

# 21. 🪟 Modal & Dialog

Modal harus menggunakan:

```text
Backdrop
+
Glass / Surface
+
Clear hierarchy
```

Recommended:

```text
max-w-md
max-w-lg
max-w-2xl
```

Modal tidak boleh terlalu besar tanpa alasan.

Struktur:

```text
Modal
│
├── Header
│   ├── Title
│   └── Close
│
├── Content
│
└── Footer
    ├── Cancel
    └── Confirm
```

---

# 22. ⏳ Loading & Skeleton

Gunakan skeleton untuk loading content yang membutuhkan waktu.

Contoh:

```tsx
<div className="
h-4
w-32
animate-pulse
rounded
bg-mc-soft
" />
```

Hindari loading spinner pada seluruh halaman jika hanya satu component yang sedang loading.

Gunakan:

> **Loading locally, not globally.**

---

# 23. 🤖 AI Interface

Maincore mendukung project AI seperti:

* LLM Application
* RAG
* AI Agent
* AI Assistant
* AI Chat
* Machine Learning Dashboard

AI interface harus tetap mengikuti Maincore UI system.

## Chat Layout

```text
AI Application
│
├── Header
│
├── Conversation
│   ├── User Message
│   ├── AI Message
│   └── AI Message
│
└── Prompt Input
```

### User Message

Gunakan primary color secara subtle.

### AI Message

Gunakan glass panel atau neutral surface.

Jangan menggunakan bubble yang terlalu besar.

---

# 24. 🧠 AI Prompt Input

Prompt input merupakan komponen utama AI application.

Recommended:

```text
Glass Container
│
├── Textarea
│
└── Action Bar
    ├── Attachment
    ├── Model
    └── Send
```

Input harus mendukung:

* Multi-line
* Loading state
* Disabled state
* Submit action
* Keyboard interaction

Send button menggunakan:

```text
mc-primary
```

---

# 25. 📎 Icon System

Gunakan satu icon library secara konsisten.

Recommended:

> **Lucide Icons**

Rules:

* Jangan mencampur banyak icon library.
* Gunakan ukuran yang konsisten.
* Default icon size: `18px` atau `20px`.
* Icon button harus memiliki accessible label.

Example:

```tsx
<Icon className="h-5 w-5" />
```

---

# 26. 🎬 Animation

Animation harus:

> **Subtle, Fast, Functional**

Recommended duration:

```text
150ms
200ms
300ms
```

Gunakan untuk:

* Hover
* Focus
* Modal
* Dropdown
* Navigation
* Loading

Hindari animasi yang mengganggu produktivitas user.

---

# 27. 🌫️ Shadow

Shadow harus soft.

Recommended:

```text
shadow-sm
shadow
shadow-md
```

Gunakan `shadow-lg` hanya untuk:

* Modal
* Dropdown
* Floating element
* Important overlay

Jangan menggunakan shadow besar pada semua card.

---

# 28. 🌈 Gradient

Gradient diperbolehkan sebagai accent.

Contoh:

```text
mc-primary → mc-dark
```

Namun gradient bukan default untuk seluruh UI.

Gunakan untuk:

* Hero
* AI visualization
* Highlight
* Decorative background
* CTA tertentu

Jangan membuat seluruh halaman menggunakan gradient.

---

# 29. ♿ Accessibility

Setiap UI Maincore harus mempertimbangkan accessibility.

### Rules

* Text harus memiliki contrast yang cukup.
* Semua interactive element harus dapat difokuskan.
* Jangan hanya mengandalkan warna.
* Button harus memiliki label yang jelas.
* Icon-only button harus memiliki `aria-label`.
* Form input harus memiliki label.
* Keyboard navigation harus bekerja.
* Focus state tidak boleh dihilangkan.

Jangan menggunakan:

```css
outline: none;
```

tanpa mengganti dengan focus indicator yang jelas.

---

# 30. 📱 Mobile First

Semua component harus dibuat:

```text
Mobile
↓
Tablet
↓
Desktop
```

Bukan sebaliknya.

Prioritaskan:

1. Content
2. Usability
3. Responsive layout
4. Decoration

---

# 31. 🧩 Component Reusability

Sebelum membuat component baru:

```text
1. Check existing components.
2. Check existing variants.
3. Reuse if possible.
4. Extend if necessary.
5. Create new component only when justified.
```

Jangan membuat:

```text
ButtonA
ButtonB
ButtonC
ButtonPrimary
ButtonBlue
ButtonMain
```

Jika sebenarnya semuanya dapat menggunakan satu reusable Button dengan variants.

Recommended:

```tsx
<Button variant="primary" />
<Button variant="secondary" />
<Button variant="outline" />
<Button variant="danger" />
```

---

# 32. 🗂️ Component Organization

Recommended:

```text
components/
│
├── ui/
│   ├── button.tsx
│   ├── input.tsx
│   ├── card.tsx
│   ├── badge.tsx
│   ├── modal.tsx
│   └── table.tsx
│
├── layout/
│   ├── navbar.tsx
│   ├── sidebar.tsx
│   └── footer.tsx
│
└── features/
    └── ...
```

`ui/` berisi reusable primitives.

`features/` berisi component yang berkaitan dengan business feature.

---

# 33. 🚫 Anti-Patterns

Jangan melakukan:

### ❌ Too Much Glass

Jangan membuat:

```text
Glass background
+
Glass card
+
Glass button
+
Glass input
+
Glass modal
```

secara bersamaan tanpa hierarchy.

### ❌ Too Many Colors

Maincore menggunakan:

```text
Base
Soft
Primary
Dark
Semantic
```

Jangan menambahkan warna baru tanpa alasan.

### ❌ Inconsistent Radius

Jangan mencampur:

```text
rounded-sm
rounded-lg
rounded-xl
rounded-2xl
rounded-3xl
rounded-full
```

secara random.

### ❌ Excessive Animation

Hindari animation yang hanya digunakan untuk dekorasi.

### ❌ Giant Typography

Hindari heading terlalu besar pada dashboard atau application UI.

---

# 34. 🧭 UI Decision Priority

Jika terjadi konflik antara visual dan usability:

```text
1. Accessibility
2. Usability
3. Readability
4. Consistency
5. Performance
6. Visual Decoration
```

Visual tidak boleh mengorbankan usability.

---

# 35. 🏗️ Recommended Page Pattern

Standard application page:

```text
┌────────────────────────────────────────────┐
│ Header                                     │
├──────────────┬─────────────────────────────┤
│              │                             │
│   Sidebar    │  Page Header                │
│              │                             │
│              │  Main Content               │
│              │                             │
│              │  ┌────────┐ ┌────────┐     │
│              │  │ Card   │ │ Card   │     │
│              │  └────────┘ └────────┘     │
│              │                             │
│              │  Content                   │
│              │                             │
└──────────────┴─────────────────────────────┘
```

Gunakan pattern ini sebagai baseline, bukan sebagai aturan mutlak.

---

# 36. 🧪 UI Quality Checklist

Sebelum feature dianggap selesai:

```text
[ ] Responsive di mobile
[ ] Responsive di desktop
[ ] Typography konsisten
[ ] Color menggunakan design token
[ ] Radius konsisten
[ ] Spacing konsisten
[ ] Glass effect digunakan secara proporsional
[ ] Hover state tersedia
[ ] Focus state tersedia
[ ] Loading state tersedia
[ ] Error state tersedia
[ ] Empty state tersedia
[ ] Accessibility diperhatikan
[ ] Tidak ada duplicate component
[ ] Tidak ada style yang tidak diperlukan
```

---

# 37. 🧠 AI Coding Instruction

Ketika AI Coding Agent bekerja di dalam project Maincore:

```text
You are working inside a Maincore-based project.

Before creating UI:

1. Inspect the existing component structure.
2. Inspect existing UI components.
3. Reuse existing components before creating new ones.
4. Follow ui.md.
5. Use the Maincore color system.
6. Use Jakarta Sans.
7. Follow the Maincore spacing system.
8. Follow the Maincore radius system.
9. Use glassmorphism consistently but avoid overusing it.
10. Keep responsive behavior by default.
11. Preserve accessibility.
12. Do not introduce unnecessary UI libraries.
13. Do not duplicate existing components.
14. Do not create new design patterns without a clear reason.
15. Prefer extending existing components over creating duplicates.

Visual hierarchy:

- Content first.
- Usability second.
- Decoration third.

When unsure:

Follow the existing project UI before introducing a new pattern.
```

---

# 38. 🔄 Project Customization

Setiap project boleh melakukan customization.

Namun customization harus tetap mempertahankan:

```text
Maincore Design Philosophy
        ↓
Maincore Color System
        ↓
Maincore Typography
        ↓
Maincore Spacing
        ↓
Maincore Component Principles
```

Project boleh menambahkan:

* Custom brand color
* Custom logo
* Custom illustration
* Custom business components
* Custom page layout

Tetapi jangan mengubah Maincore design language tanpa alasan yang jelas.

---

# 39. 📌 Maincore UI Golden Rules

```text
01. Keep it clean.
02. Keep it consistent.
03. Keep it reusable.
04. Keep it responsive.
05. Keep it accessible.
06. Use glassmorphism with restraint.
07. Use blue as the primary visual identity.
08. Use Jakarta Sans as the default typography.
09. Reuse components before creating new ones.
10. Never sacrifice usability for decoration.
```

---

# 40. 🎯 Final Principle

Maincore UI bukan bertujuan membuat semua project terlihat **100% sama**.

Tujuannya adalah membuat semua project memiliki **design foundation yang sama**.

```text
                    MAINCORE UI
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       COLORS       TYPOGRAPHY      COMPONENTS
          │              │              │
          └──────────────┼──────────────┘
                         │
                    DESIGN SYSTEM
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       E-Commerce    AI Application   SaaS
          │              │              │
          └──────────────┼──────────────┘
                         │
                  PROJECT IDENTITY
```

> **Maincore provides the foundation.**
>
> **Each project provides the identity.**

---

# 🚀 Maincore UI Philosophy

```text
Modern.
Clean.
Consistent.
Reusable.
Accessible.
Responsive.

Glass where it matters.

Blue where it matters.

Content always comes first.

Clone.
Configure.
Design.
Build.
```
