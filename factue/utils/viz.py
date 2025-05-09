import pandas as pd

# Set display options
pd.set_option("display.max_colwidth", 200)  # Set max column width
pd.set_option("display.expand_frame_repr", False)  # Avoid frame splitting
# pd.set_option("display.max_rows", None)  # Show all rows if needed

# # Display selected columns with wrapping
# from IPython.display import HTML, display


def disp(df, limit=None):
    if limit is None:
        limit = len(df)

    # Create a dictionary of column styles to restrict column width
    column_styles = [
        {
            "selector": f"th.col{i}",
            "props": [
                ("max-width", "12cm"),
                ("white-space", "pre-wrap"),
                ("word-wrap", "break-word"),
            ],
        }
        for i in range(len(df.columns))
    ] + [
        {
            "selector": f"td.col{i}",
            "props": [
                ("max-width", "12cm"),
                ("white-space", "pre-wrap"),
                ("word-wrap", "break-word"),
            ],
        }
        for i in range(len(df.columns))
    ]

    return (
        df.head(limit)
        .style.set_properties(
            subset=df.columns,
            **{
                "white-space": "pre-wrap",
                "word-wrap": "break-word",
                "text-align": "left",
            },
        )
        .set_table_styles(column_styles)
    )


# def disp(df, limit=None):
#     # Create a style with wrapped text in selected columns
#     if limit is None:
#         limit = len(df)
#     return df.head(limit).style.set_properties(
#         subset=df.columns,
#         **{
#             "white-space": "pre-wrap",
#             "word-wrap": "break-word",
#             "text-align": "left",
#         }
#     )
