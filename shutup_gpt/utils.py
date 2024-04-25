import streamlit.components.v1 as components

def scroll_to_bottom():
    components.html("""
    <script>
    setTimeout(() => {
        document.querySelectorAll('*').forEach(el => {
            if (el.scrollHeight > el.clientHeight) {
                el.scrollTop = el.scrollHeight;
            }
        });
    }, 1000); // Small delay to ensure the DOM has loaded
    </script>
    """, height=0)
