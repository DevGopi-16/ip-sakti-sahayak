
import {
Layers,
FileText,
Award,
MapPin,
Leaf,
Copyright,
} from 'lucide-react';

export const STATUTE_GROUPS = [
{
title: 'GLOBAL',
subtitle: 'All statutory documents',
items: [
{
code: 'ALL',
label: 'All Documents',
icon: Layers,
},
],
},

{
title: 'INTELLECTUAL PROPERTY',
subtitle: 'Core IP legislation',
items: [
{
code: 'PA',
label: 'Patents Act, 1970',
icon: FileText,
},
{
code: 'TM',
label: 'Trademarks Act, 1999',
icon: Award,
},
{
code: 'GI',
label: 'GI Act, 1999',
icon: MapPin,
},
{
code: 'BD',
label: 'Biodiversity Act, 2002',
icon: Leaf,
},
{
code: 'CR',
label: 'Copyright Act, 1957',
icon: Copyright,
},
{
code: 'DS',
label: 'Designs Act, 2000',
icon: FileText,
},
],
},



{
title: 'DRUGS & TRADITIONAL KNOWLEDGE',
subtitle: 'Traditional medicine & regulatory law',
items: [
{
code: 'DC',
label: 'Drugs & Cosmetics Act, 1940',
icon: FileText,
},
{
code: 'DR',
label: 'Drugs & Cosmetics Rules, 1945',
icon: FileText,
},
{
code: 'TMS',
label: 'Traditional Medicine Strategy 2014–2023',
icon: FileText,
},
],
},
];

export const INITIAL_BOT_MESSAGE = {
sender: 'bot',
text:
'Namaste! I am **IP-SAKTI Sahayak**, your AI Legal Assistant for Indian Intellectual Property and Traditional Knowledge (Ayurveda) laws.\n\nHow can I help you today?',
sources: [],
};

export const QUICK_PROMPTS = [
{
cite: '§3(p)',
text:
'What is Section 3(p) under the Indian Patents Act?',
},
{
cite: 'TK',
text:
'Can traditional Ayurvedic formulations be patented in India?',
},
{
cite: 'GI Act',
text:
'What are the requirements for Geographical Indications under GI Act 1999?',
},
];
