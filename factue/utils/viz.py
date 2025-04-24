import pandas as pd

# Set display options
pd.set_option("display.max_colwidth", 200)  # Set max column width
pd.set_option("display.expand_frame_repr", False)  # Avoid frame splitting
# pd.set_option("display.max_rows", None)  # Show all rows if needed

# # Display selected columns with wrapping
# from IPython.display import HTML, display


def disp(df):
    # Create a style with wrapped text in selected columns
    return df.style.set_properties(
        subset=df.columns,
        **{
            "white-space": "pre-wrap",
            "word-wrap": "break-word",
            "text-align": "left",
        }
    )
