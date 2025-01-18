import pytest
from requests_html import HTML, StructuredExtractor, ExtractorPattern

@pytest.fixture
def sample_html():
    return HTML(html='''
        <div class="container">
            <div class="product-card">
                <h2 class="product-title">iPhone 14</h2>
                <span class="price">$999</span>
                <p class="description">Latest iPhone model</p>
            </div>
            <div class="product-card">
                <h2 class="product-title">Samsung Galaxy S23</h2>
                <span class="price">$899</span>
                <p class="description">Flagship Android phone</p>
            </div>
            <div class="product-card">
                <h2 class="product-title">Google Pixel 7</h2>
                <!-- Missing price -->
                <p class="description">Google's flagship phone</p>
            </div>
        </div>
    ''')

@pytest.fixture
def basic_pattern():
    return ExtractorPattern(
        selector=".product-card",
        fields={
            "title": ".product-title",
            "price": ".price",
            "description": ".description"
        }
    )

@pytest.fixture
def pattern_with_required():
    return ExtractorPattern(
        selector=".product-card",
        fields={
            "title": ".product-title",
            "price": ".price",
            "description": ".description"
        },
        required_fields=["title", "price"]
    )

def test_extractor_initialization(sample_html):
    extractor = StructuredExtractor(sample_html)
    assert extractor.html == sample_html

def test_basic_extraction(sample_html, basic_pattern):
    extractor = StructuredExtractor(sample_html)
    results = extractor.extract_structured_data(basic_pattern)
    
    assert len(results) == 3
    assert results[0]["title"] == "iPhone 14"
    assert results[0]["price"] == "$999"
    assert results[0]["description"] == "Latest iPhone model"

def test_extraction_with_required_fields(sample_html, pattern_with_required):
    extractor = StructuredExtractor(sample_html)
    results = extractor.extract_structured_data(pattern_with_required)
    
    # Should only return 2 items since the third is missing the required price
    assert len(results) == 2
    assert all("price" in item for item in results)

def test_extraction_with_limit(sample_html, basic_pattern):
    extractor = StructuredExtractor(sample_html)
    results = extractor.extract_structured_data(basic_pattern, limit=1)
    
    assert len(results) == 1
    assert results[0]["title"] == "iPhone 14"

def test_missing_optional_field(sample_html):
    pattern = ExtractorPattern(
        selector=".product-card",
        fields={
            "title": ".product-title",
            "nonexistent": ".nonexistent-class"
        }
    )
    
    extractor = StructuredExtractor(sample_html)
    results = extractor.extract_structured_data(pattern)
    
    assert len(results) == 3
    assert all(item["nonexistent"] == "" for item in results)

def test_invalid_selector(sample_html):
    pattern = ExtractorPattern(
        selector=".nonexistent-container",
        fields={
            "title": ".product-title"
        }
    )
    
    extractor = StructuredExtractor(sample_html)
    results = extractor.extract_structured_data(pattern)
    
    assert len(results) == 0

def test_empty_html():
    """Test extraction with empty HTML"""
    html = HTML(html='<div></div>')
    extractor = StructuredExtractor(html)
    
    pattern = ExtractorPattern(
        selector=".product-card",
        fields={
            "title": ".product-title"
        }
    )
    
    results = extractor.extract_structured_data(pattern)
    assert len(results) == 0

def test_pattern_without_required_fields():
    """Test pattern initialization without required fields"""
    pattern = ExtractorPattern(
        selector=".product-card",
        fields={
            "title": ".product-title"
        }
    )
    assert pattern.required_fields is None

def test_from_url(requests_mock):
    """Test creating extractor from URL"""
    html_content = '''
        <div class="product-card">
            <h2 class="product-title">Test Product</h2>
            <span class="price">$100</span>
        </div>
    '''
    requests_mock.get("https://example.com", text=html_content)
    
    extractor = StructuredExtractor.from_url("https://example.com")
    assert isinstance(extractor, StructuredExtractor)
    
    pattern = ExtractorPattern(
        selector=".product-card",
        fields={
            "title": ".product-title",
            "price": ".price"
        }
    )
    
    results = extractor.extract_structured_data(pattern)
    assert len(results) == 1
    assert results[0]["title"] == "Test Product"
    assert results[0]["price"] == "$100"