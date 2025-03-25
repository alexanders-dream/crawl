# content_generator.py
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_output(llm: Any, task: str, form_data: Dict[str, str]) -> str:
    """Generate task-specific marketing content"""
    task_prompts = {
    "Marketing Strategy": """
        You are a senior marketing strategist tasked with creating a comprehensive marketing plan.
        
        ## Business Context
        Brand Description: {brand_description}
        Target Audience: {target_audience}
        Products/Services: {products_services}
        Marketing Goals: {marketing_goals}
        Existing Content: {existing_content}
        Keywords: {keywords}
        
        ## Instructions
        Develop a detailed, actionable marketing strategy that aligns with the business goals.
        Focus on creating a strategy that is specific, measurable, achievable, relevant, and time-bound.
        
        ## Required Output Structure
        1. Executive Summary (brief overview of the entire strategy)
        2. Market Analysis (industry trends, competitive landscape)
        3. Target Audience Segmentation (detailed profiles of key segments)
        4. Value Proposition & Positioning (unique selling points, brand positioning)
        5. Marketing Channels & Tactics (prioritized by ROI potential)
        6. Content Strategy (topics, formats, distribution, calendar)
        7. Budget Allocation (recommended spending by channel)
        8. Implementation Timeline (30-60-90 day plan)
        9. KPIs & Success Metrics (specific measurements for each goal)
        10. Risk Assessment & Contingency Plans
    """,
    
    "Campaign Strategy": """
        You are a creative campaign director tasked with developing innovative marketing campaigns.
        
        ## Business Context
        Brand Description: {brand_description}
        Target Audience: {target_audience}
        Products/Services: {products_services}
        Marketing Goals: {marketing_goals}
        Keywords: {keywords}
        Selected Topics: {suggested_topics}
        Tone: {tone}
        
        ## Instructions
        Generate 5 distinct, creative campaign concepts that align with the brand identity and will resonate with the target audience.
        Each campaign should be achievable with realistic resources and have clear business impact.
        
        ## Required Output Structure
        For each of the 5 campaigns, provide:
        
        ### Campaign [Number]: [Creative Name]
        * Concept: Brief explanation of the campaign idea and creative angle
        * Target Segment: Specific audience segment this will appeal to most
        * Core Message: The primary takeaway for the audience
        * Campaign Elements: List of deliverables (videos, posts, emails, etc.)
        * Channels: Primary platforms for distribution
        * Timeline: Suggested duration and key milestones
        * Success Metrics: How to measure campaign effectiveness
        * Estimated Impact: Expected outcomes tied to marketing goals
    """,
    
    "Social Media Content Strategy": """
        You are an expert social media manager creating platform-specific content.
        
        ## Business Context
        Brand Description: {brand_description}
        Target Audience: {target_audience}
        Products/Services: {products_services}
        Marketing Goals: {marketing_goals}
        Keywords: {keywords}
        Selected Topics: {suggested_topics}
        Tone: {tone}
        Post Type: {post_type}
        
        ## Instructions
        Create a comprehensive social media content plan optimized for {post_type}.
        Focus on engaging the target audience with content that drives specific marketing goals.
        Ensure all content maintains the brand's {tone} tone of voice.
        
        ## Required Output Structure
        1. Platform Strategy
           * Why {post_type} is effective for this audience
           * Best practices specific to this platform
           * Posting frequency recommendations
        
        2. Content Pillars (3-4 key themes aligned with business goals)
        
        3. Content Calendar (2-week sample)
           * Week 1:
             * Day 1: [Content type] - [Example post with exact copy]
             * Day 2: [Content type] - [Example post with exact copy]
             [Continue for all week]
           * Week 2: [Same format]
        
        4. Engagement Strategy
           * Response templates for common interactions
           * Community-building tactics
           * User-generated content opportunities
        
        5. Growth Tactics
           * Hashtag strategy (10-15 targeted hashtags grouped by purpose)
           * Collaboration opportunities
           * Cross-promotion ideas
        
        6. Analytics Focus
           * Key metrics to track for this specific platform
           * Benchmarks for success
    """,
    
    "SEO Optimization Strategy": """
        You are an SEO specialist developing a comprehensive search optimization strategy.
        
        ## Business Context
        Brand Description: {brand_description}
        Target Audience: {target_audience}
        Products/Services: {products_services}
        Marketing Goals: {marketing_goals}
        Keywords: {keywords}
        Existing Content: {existing_content}
        
        ## Instructions
        Create a detailed SEO strategy that will improve organic visibility and drive qualified traffic.
        Focus on both quick wins and long-term sustainable growth.
        Provide specific, actionable recommendations rather than general advice.
        
        ## Required Output Structure
        1. Keyword Strategy
           * Primary Keywords (5-7 high-priority terms with search volume estimates)
           * Secondary Keywords (10-15 supporting terms)
           * Long-tail Opportunities (7-10 specific phrases)
           * Semantic/Topic Clusters (group related terms by topic)
        
        2. On-Page Optimization
           * Title Tag Templates
           * Meta Description Frameworks
           * Heading Structure Recommendations
           * Content Length and Formatting Guidelines
           * Internal Linking Strategy
        
        3. Technical SEO Checklist
           * Site Speed Optimization
           * Mobile Usability
           * Schema Markup Recommendations
           * Indexation Controls
           * URL Structure Guidelines
        
        4. Content Strategy
           * Content Gaps Analysis
           * Content Update Priorities
           * New Content Recommendations (5-7 specific pieces)
           * Content Calendar Framework
        
        5. Off-Page Strategy
           * Link Building Tactics (specific to industry)
           * Digital PR Opportunities
           * Local Citation Opportunities (if applicable)
        
        6. Measurement Plan
           * Key Performance Indicators
           * Tracking Setup Recommendations
           * Reporting Schedule and Format
        """,

    "Post Composer": """
        You are a professional real estate copywriter creating compelling property listings and promotional content.
        
        ## Business Context
        Brand Description: {brand_description}
        Target Audience: {target_audience}
        Properties: {properties_data}
        Marketing Goals: {marketing_goals}
        Keywords: {keywords}
        Selected Topics: {suggested_topics}
        
        ## Instructions
        Create engaging property posts that highlight key features and attract potential buyers/renters.
        Include property details from {properties_data} and incorporate {keywords} naturally.
        Maintain a {tone} tone while emphasizing unique selling points.
        
        ## Property Post Structure
        1. Property Image: {property_image_url}
        2. Headline: Attention-grabbing title with location and key feature
        3. Description:
           - Opening hook highlighting unique feature
           - Key details (bedrooms, bathrooms, sqft, amenities)
           - Neighborhood highlights
           - Unique selling points
        4. Call-to-Action: Clear next steps (schedule viewing, contact agent)
        5. Hashtags: 5-10 relevant real estate hashtags
        
        ## Platform-Specific Guidelines
        ### Instagram:
        - Use high-quality property images
        - Caption under 150 words highlighting key features
        - Include price and location in first line
        - Use emojis sparingly for emphasis
        - Hashtags: #realestate #property #location #homesforsale
        
        ### Facebook:
        - Longer description (200-300 words)
        - Include virtual tour link if available
        - Highlight community amenities
        - Use bullet points for key features
        
        ### LinkedIn:
        - Professional tone focusing on investment potential
        - Include market trends and comparisons
        - Target investors and professionals
        - Use statistics and data points
        
        ## Required Output
        {
            "image_url": "{property_image_url}",
            "headline": "Attention-grabbing property title",
            "description": "Detailed property description...",
            "cta": "Schedule a viewing today!",
            "hashtags": ["#realestate", "#property", ...]
        }
        """
    }
    
    try:
        # Create the prompt
        prompt = ChatPromptTemplate.from_template(task_prompts[task])
        
        # Create the chain
        chain = prompt | llm | StrOutputParser()
        
        # Execute the chain
        response = chain.invoke(form_data)
        
        return response
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        return f"Error generating content: {str(e)}"
