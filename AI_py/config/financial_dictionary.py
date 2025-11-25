"""
Financial Dictionary for AI Model Reference

This dictionary provides financial terminology, definitions, and phrase mappings
to help the AI model better understand user queries and map them to appropriate tools.
"""

from typing import Dict, List, Set

class FinancialDictionary:
    """Financial terminology and phrase mappings for AI understanding."""
    
    # Expense Categories and Synonyms
    CATEGORY_SYNONYMS: Dict[str, List[str]] = {
        'groceries': ['groceries', 'grocery', 'food shopping', 'supermarket', 'market', 'food store', 'produce'],
        'rent': ['rent', 'rental', 'housing', 'apartment', 'lease', 'monthly rent'],
        'utilities': ['utilities', 'utility', 'electric', 'electricity', 'water', 'gas bill', 'power', 'energy'],
        'gas': ['gas', 'fuel', 'petrol', 'gasoline', 'filling station', 'gas station'],
        'dining': ['dining', 'dining out', 'restaurant', 'restaurants', 'eating out', 'food', 'meal', 'meals'],
        'coffee': ['coffee', 'cafe', 'café', 'coffee shop', 'starbucks', 'latte'],
        'entertainment': ['entertainment', 'movies', 'cinema', 'theater', 'theatre', 'streaming', 'netflix', 'spotify'],
        'transportation': ['transportation', 'transport', 'uber', 'lyft', 'taxi', 'public transport', 'transit'],
        'shopping': ['shopping', 'retail', 'store', 'stores', 'purchase', 'purchases'],
        'healthcare': ['healthcare', 'medical', 'doctor', 'pharmacy', 'medicine', 'prescription', 'hospital'],
        'insurance': ['insurance', 'premium', 'coverage', 'policy'],
        'subscription': ['subscription', 'subscriptions', 'membership', 'memberships', 'recurring'],
        'education': ['education', 'tuition', 'school', 'course', 'courses', 'training'],
        'personal': ['personal', 'misc', 'miscellaneous', 'other', 'general'],
    }
    
    # Financial Terms and Definitions
    FINANCIAL_TERMS: Dict[str, str] = {
        'expense': 'A cost or expenditure, typically money spent on goods or services',
        'income': 'Money received, especially on a regular basis, for work or investments',
        'budget': 'An estimate of income and expenditure for a set period of time',
        'spending': 'The act of paying out money; expenditure',
        'total': 'The sum of all amounts',
        'average': 'A value representing the mean of a set of values',
        'largest': 'The greatest in amount, size, or value',
        'smallest': 'The least in amount, size, or value',
        'category': 'A class or division of expenses grouped by type',
        'monthly': 'Relating to or occurring every month',
        'annual': 'Relating to or occurring every year',
        'percentage': 'A rate, number, or amount in each hundred',
        'ratio': 'The quantitative relation between two amounts showing the number of times one value contains or is contained within the other',
        'trend': 'A general direction in which something is developing or changing',
        'comparison': 'The act of comparing two or more things',
    }
    
    # Query Intent Mappings
    INTENT_KEYWORDS: Dict[str, List[str]] = {
        'largest_expense': ['largest', 'biggest', 'highest', 'most expensive', 'max', 'maximum', 'top expense'],
        'smallest_expense': ['smallest', 'lowest', 'minimum', 'min', 'cheapest', 'least expensive'],
        'total_spending': ['total', 'sum', 'how much', 'spent', 'spend', 'all expenses', 'everything'],
        'category_spending': ['spending on', 'spent on', 'how much for', 'cost of', 'expenses for'],
        'average_expense': ['average', 'mean', 'avg', 'typical', 'usual'],
        'monthly_average': ['monthly average', 'average per month', 'monthly spending average', 'avg monthly'],
        'category_percentage': ['percentage', 'percent', '%', 'portion', 'share', 'how much of'],
        'expense_ratio': ['ratio', 'proportion', 'compare', 'relative to'],
        'expense_count': ['count', 'how many', 'number of', 'total expenses'],
        'top_categories': ['top categories', 'spending most', 'categories', 'which category', 'spend most on'],
        'compare_months': ['compare', 'comparison', 'vs', 'versus', 'this month vs', 'last month vs'],
        'trend': ['trend', 'over time', 'pattern', 'change', 'increasing', 'decreasing'],
    }
    
    # Time-related Phrases
    TIME_PHRASES: Dict[str, List[str]] = {
        'today': ['today', 'this day', 'current day'],
        'yesterday': ['yesterday', 'previous day'],
        'this_week': ['this week', 'current week', 'past week'],
        'last_week': ['last week', 'previous week', 'past week'],
        'this_month': ['this month', 'current month', 'present month'],
        'last_month': ['last month', 'previous month', 'past month'],
        'this_year': ['this year', 'current year', 'present year'],
        'last_year': ['last year', 'previous year', 'past year'],
    }
    
    # Amount Phrases
    AMOUNT_PHRASES: Dict[str, List[str]] = {
        'exact_amount': ['exactly', 'precisely', 'exact'],
        'approximately': ['about', 'around', 'approximately', 'roughly', '~'],
        'at_least': ['at least', 'minimum', 'no less than'],
        'at_most': ['at most', 'maximum', 'no more than', 'up to'],
    }
    
    # Question Patterns
    QUESTION_PATTERNS: List[str] = [
        r"what'?s?\s+(?:my|the)\s+",
        r"how\s+much\s+",
        r"how\s+many\s+",
        r"which\s+",
        r"where\s+",
        r"when\s+",
        r"show\s+me\s+",
        r"tell\s+me\s+",
        r"list\s+",
        r"compare\s+",
    ]
    
    @classmethod
    def get_category_synonyms(cls, category: str) -> List[str]:
        """Get all synonyms for a category."""
        category_lower = category.lower()
        for key, synonyms in cls.CATEGORY_SYNONYMS.items():
            if category_lower == key or category_lower in synonyms:
                return [key] + synonyms
        return [category]
    
    @classmethod
    def find_category(cls, phrase: str) -> str:
        """Find the category that matches a phrase."""
        phrase_lower = phrase.lower()
        for category, synonyms in cls.CATEGORY_SYNONYMS.items():
            if phrase_lower == category or phrase_lower in synonyms:
                return category
        return phrase_lower  # Return as-is if no match
    
    @classmethod
    def get_intent_keywords(cls, intent: str) -> List[str]:
        """Get keywords for a specific intent."""
        return cls.INTENT_KEYWORDS.get(intent, [])
    
    @classmethod
    def detect_intent(cls, query: str) -> List[str]:
        """Detect possible intents from a query."""
        query_lower = query.lower()
        detected = []
        for intent, keywords in cls.INTENT_KEYWORDS.items():
            if any(keyword in query_lower for keyword in keywords):
                detected.append(intent)
        return detected
    
    @classmethod
    def get_financial_term_definition(cls, term: str) -> str:
        """Get definition for a financial term."""
        return cls.FINANCIAL_TERMS.get(term.lower(), '')
    
    @classmethod
    def expand_query(cls, query: str) -> Dict[str, any]:
        """Expand a query with detected intents, categories, and time references."""
        query_lower = query.lower()
        
        result = {
            'original_query': query,
            'intents': cls.detect_intent(query),
            'categories': [],
            'time_references': [],
            'amount_phrases': [],
        }
        
        # Detect categories
        for category, synonyms in cls.CATEGORY_SYNONYMS.items():
            if any(syn in query_lower for syn in synonyms):
                result['categories'].append(category)
        
        # Detect time references
        for time_key, phrases in cls.TIME_PHRASES.items():
            if any(phrase in query_lower for phrase in phrases):
                result['time_references'].append(time_key)
        
        # Detect amount phrases
        for amount_key, phrases in cls.AMOUNT_PHRASES.items():
            if any(phrase in query_lower for phrase in phrases):
                result['amount_phrases'].append(amount_key)
        
        return result

