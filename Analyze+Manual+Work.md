

```python
import pandas as pd
import re
import matplotlib.pyplot as plt
%matplotlib inline
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)


def bar_chart(labels, values, title, xaxis = '', yaxis = '', xsize = 14, subtitle=''):
    d = [go.Bar(
            x=labels,
            y=values,
            text=values,
            textposition = 'outside',
            opacity=1)]

    layout = go.Layout(
        title='<b>'+title+'</b><br>'+subtitle,
        xaxis=dict(
            title=xaxis,
            tickfont=dict(
                size=xsize,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title=yaxis,
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
    )

    fig = go.Figure(data=d, layout=layout)
    iplot(fig, filename='color-bar')
    
def viz(groupby_df, title = '', xaxis = '', yaxis = '', xsize = 14, subtitle=''):
    labels = list(groupby_df.index)
    values = list(groupby_df.values)
    
    d = [go.Bar(
            x=labels,
            y=values,
            text=values,
            textposition = 'outside',
            opacity=1)]

    layout = go.Layout(
        title='<b>'+title+'</b><br>'+subtitle,
        xaxis=dict(
            title=xaxis,
            tickfont=dict(
                size=xsize,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title=yaxis,
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
    )

    fig = go.Figure(data=d, layout=layout)
    iplot(fig, filename='color-bar')
```


<script>requirejs.config({paths: { 'plotly': ['https://cdn.plot.ly/plotly-latest.min']},});if(!window.Plotly) {{require(['plotly'],function(plotly) {window.Plotly=plotly;});}}</script>



```python
data = pd.read_excel('CoC__Departments_Research_TK_030918_Edits.xlsx', encoding = 'iso-8859-1')
```


```python
data.columns
```




    Index(['index', 'City Department', 'Webpage Title', 'URL', 'Persona', 'Verb',
           'SVC in URL?', 'Button Present?', 'i_want_to', 'nav',
           'No. of E-mail Addresses', 'E-mail Address ', 'PDF Count',
           'External Link Count', 'External Link URL(s)', 'Top Words'],
          dtype='object')




```python
columns = ['index', 'dept', 'title', 'url', 'persona', 'verb',
       'service', 'button', 'i_want_to', 'nav',
       'email_count', 'emails', 'pdf_count',
       'external_count', 'external_urls', 'top_words']
data.columns = columns
```


```python
data1 = data[(data['dept'] == 'Department of Business Affairs and Consumer Protection') | (data['dept'] == 'Department of Finance')].set_index(keys='index').reset_index(drop=True)
data1 = data1.fillna('NA')
data1['verb'] = data1.verb.apply(lambda x: x.strip())
```


```python
data1.verb.unique()
```




    array(['Apply', 'Pay', 'View', 'Register', 'File', 'Learn', 'Multiple',
           'Obtain', 'Enroll', 'Request', 'Find', 'Report', 'Other', 'NA'], dtype=object)




```python
verbs = set()
for words in data1.verb.unique():
    for wor in re.split('W+ |;', words):
        verbs.add(wor.strip())
verbs
```




    {'Apply',
     'Enroll',
     'File',
     'Find',
     'Learn',
     'Multiple',
     'NA',
     'Obtain',
     'Other',
     'Pay',
     'Register',
     'Report',
     'Request',
     'View'}




```python
data1['verb_list'] = data1.verb.apply(lambda x: re.split('W+ | ;|; |,|;',x.strip()))
```


```python
data1['verb_cnt'] = data1.verb_list.apply(lambda x: len(x))
```


```python
data1.groupby('verb_cnt').size()
```




    verb_cnt
    1    604
    dtype: int64




```python
data_single = data1[data1['verb_cnt'] == 1]
business = data_single[data_single.dept == 'Department of Business Affairs and Consumer Protection']
finance = data_single[data_single.dept == 'Department of Finance']
business_df = business.groupby('verb').size().sort_values(ascending=False)
finance_df = finance.groupby('verb').size().sort_values(ascending=False)
viz(business_df,'Number of Webpages by Verb for Department of Business Affairs and Consumer Protection','Verb','Number of Webpages')
print('Based on manual categorization, BACP pages were categorized into the above verb categories.')
viz(finance_df,'<b>Number of Webpages by Verb for Department of Finance', 'Verb', 'Number of Webpages',12)
print('Based on manual categorization, DoF pages were categorized into the above verb categories.')
```


<div id="379b3cc4-1a45-4890-b619-8003fe2698da" style="height: 525px; width: 100%;" class="plotly-graph-div"></div><script type="text/javascript">require(["plotly"], function(Plotly) { window.PLOTLYENV=window.PLOTLYENV || {};window.PLOTLYENV.BASE_URL="https://plot.ly";Plotly.newPlot("379b3cc4-1a45-4890-b619-8003fe2698da", [{"type": "bar", "x": ["Learn", "File", "View", "Apply", "NA", "Multiple", "Obtain", "Request", "Register", "Find", "Other"], "y": [230, 16, 12, 11, 5, 5, 4, 3, 3, 3, 1], "text": [230, 16, 12, 11, 5, 5, 4, 3, 3, 3, 1], "textposition": "outside", "opacity": 1}], {"title": "<b>Number of Webpages by Verb for Department of Business Affairs and Consumer Protection</b><br>", "xaxis": {"title": "Verb", "tickfont": {"size": 14, "color": "rgb(107, 107, 107)"}}, "yaxis": {"title": "Number of Webpages", "titlefont": {"size": 16, "color": "rgb(107, 107, 107)"}, "tickfont": {"size": 14, "color": "rgb(107, 107, 107)"}}}, {"showLink": true, "linkText": "Export to plot.ly"})});</script>


    Based on manual categorization, BACP pages were categorized into the above verb categories.
    


<div id="537f06a6-aa1c-4570-ad6d-172aa5e595a0" style="height: 525px; width: 100%;" class="plotly-graph-div"></div><script type="text/javascript">require(["plotly"], function(Plotly) { window.PLOTLYENV=window.PLOTLYENV || {};window.PLOTLYENV.BASE_URL="https://plot.ly";Plotly.newPlot("537f06a6-aa1c-4570-ad6d-172aa5e595a0", [{"type": "bar", "x": ["Learn", "Obtain", "View", "NA", "File", "Apply", "Enroll", "Request", "Pay", "Find", "Report", "Multiple"], "y": [183, 34, 21, 21, 16, 14, 5, 4, 4, 4, 3, 2], "text": [183, 34, 21, 21, 16, 14, 5, 4, 4, 4, 3, 2], "textposition": "outside", "opacity": 1}], {"title": "<b><b>Number of Webpages by Verb for Department of Finance</b><br>", "xaxis": {"title": "Verb", "tickfont": {"size": 12, "color": "rgb(107, 107, 107)"}}, "yaxis": {"title": "Number of Webpages", "titlefont": {"size": 16, "color": "rgb(107, 107, 107)"}, "tickfont": {"size": 14, "color": "rgb(107, 107, 107)"}}}, {"showLink": true, "linkText": "Export to plot.ly"})});</script>


    Based on manual categorization, DoF pages were categorized into the above verb categories.
    

## Webpages Per Agency


```python
web_per_dept = data.groupby('dept').size().sort_values(ascending=False)
values = list(web_per_dept.values)
depts = list(web_per_dept.index)
```


```python
bar_chart(depts[1:], values[1:], 'Webpages per Department','Department', 'Number of Webpages',8)
```


<div id="76fe13d9-b46f-4c20-a738-c5a17edeae29" style="height: 525px; width: 100%;" class="plotly-graph-div"></div><script type="text/javascript">require(["plotly"], function(Plotly) { window.PLOTLYENV=window.PLOTLYENV || {};window.PLOTLYENV.BASE_URL="https://plot.ly";Plotly.newPlot("76fe13d9-b46f-4c20-a738-c5a17edeae29", [{"type": "bar", "x": ["Department of Cultural Affairs and Special Events", "Department of Planning and Development", "Department of Finance", "Department of Procurement Services", "Department of Business Affairs and Consumer Protection", "Department of Public Health", "Department of Family & Support Services", "Department of Transportation", "Office of the Mayor", "Department of Buildings", "Department of Law", "Department of Streets and Sanitation", "Department of Water Management", "Board of Ethics", "Department of Human Resources", "Department of Innovation and Technology", "Emergency Management & Communications", "Mayor's Office for People with Disabilities", "Other", "Office of Budget and Management", "Commission on Human Relations", "Department of Administrative Hearings", "Chicago Fire Department", "Department of Animal Care and Control", "Department of Fleet and Facility Management", "311 City Services", "License Appeal Commission", "Chicago Police Board", "Chicago Police Department", "Chicago Public Library", "City of Chicago TV", "Office of the Inspector General", "Department of Aviation", "Civilian Office of Police Accountability", "Department of Compliance"], "y": [600, 546, 311, 299, 294, 288, 198, 196, 186, 175, 161, 158, 149, 137, 126, 100, 96, 92, 72, 70, 59, 57, 54, 49, 45, 27, 24, 20, 19, 16, 12, 12, 11, 9, 1], "text": [600, 546, 311, 299, 294, 288, 198, 196, 186, 175, 161, 158, 149, 137, 126, 100, 96, 92, 72, 70, 59, 57, 54, 49, 45, 27, 24, 20, 19, 16, 12, 12, 11, 9, 1], "textposition": "outside", "opacity": 1}], {"title": "<b>Webpages per Department</b><br>", "xaxis": {"title": "Department", "tickfont": {"size": 8, "color": "rgb(107, 107, 107)"}}, "yaxis": {"title": "Number of Webpages", "titlefont": {"size": 16, "color": "rgb(107, 107, 107)"}, "tickfont": {"size": 14, "color": "rgb(107, 107, 107)"}}}, {"showLink": true, "linkText": "Export to plot.ly"})});</script>


## Personas


```python
b_personas = {}
for row in business.persona.apply(lambda x: re.split(';',x)):
    for persona in row:
        if persona not in b_personas:
            b_personas[persona] = 1
        else:
            b_personas[persona] += 1
f_personas = {}    
for row in finance.persona.apply(lambda x: re.split(';',x)):
    for persona in row:
        if persona not in f_personas:
            f_personas[persona] = 1
        else:
            f_personas[persona] += 1
```


```python
f_list = list(f_personas.items())
b_list = list(b_personas.items())
f_list.sort(key=lambda x: x[1])
f_list = f_list[::-1]
b_list.sort(key=lambda x: x[1])
b_list = b_list[::-1]
f_persona_list = [x for x,y in f_list]
f_count_list = [y for x,y in f_list]
b_persona_list = [x for x,y in b_list]
b_count_list = [y for x,y in b_list]
bar_chart(f_persona_list[:20],f_count_list[:20],"Dept. of Finance Persona Appearances",xsize=11)
bar_chart(b_persona_list[:20],b_count_list[:20],"Dept. of Business Affairs and Consumer<br>Protection Persona Appearances",xsize=11)
```


<div id="23ce662c-dc7b-4937-9ead-348bc95649ab" style="height: 525px; width: 100%;" class="plotly-graph-div"></div><script type="text/javascript">require(["plotly"], function(Plotly) { window.PLOTLYENV=window.PLOTLYENV || {};window.PLOTLYENV.BASE_URL="https://plot.ly";Plotly.newPlot("23ce662c-dc7b-4937-9ead-348bc95649ab", [{"type": "bar", "x": ["Constituent", "City Employee", "General", "Business", "Business Owner", "Red Light Ticket Recipient", "Property Owner", "Vehicle Owner", "Parking Ticket Recipient", "NA", "Motorist", "Consumer", "Automated Speed Enforcement Ticket Recipient", "tax collector", "Government Official", "Motorists", "Tax payer", "Retailer", "Drivers", "N/A - Rollup"], "y": [79, 29, 22, 17, 17, 14, 14, 13, 13, 12, 12, 11, 11, 9, 9, 8, 8, 8, 7, 5], "text": [79, 29, 22, 17, 17, 14, 14, 13, 13, 12, 12, 11, 11, 9, 9, 8, 8, 8, 7, 5], "textposition": "outside", "opacity": 1}], {"title": "<b>Dept. of Finance Persona Appearances</b><br>", "xaxis": {"title": "", "tickfont": {"size": 11, "color": "rgb(107, 107, 107)"}}, "yaxis": {"title": "", "titlefont": {"size": 16, "color": "rgb(107, 107, 107)"}, "tickfont": {"size": 14, "color": "rgb(107, 107, 107)"}}}, {"showLink": true, "linkText": "Export to plot.ly"})});</script>



<div id="166196fb-ca47-45a3-ac4a-e646908e0f65" style="height: 525px; width: 100%;" class="plotly-graph-div"></div><script type="text/javascript">require(["plotly"], function(Plotly) { window.PLOTLYENV=window.PLOTLYENV || {};window.PLOTLYENV.BASE_URL="https://plot.ly";Plotly.newPlot("166196fb-ca47-45a3-ac4a-e646908e0f65", [{"type": "bar", "x": ["Business Owner", "Constituent", "Consumer", "Bilingual Business Owner", "Potential Business Owner", "Tourist", "Visitor", "Business Owners", "Employer", "Shared Housing Unit Operator", "Short Term Rental Intermediary", "Employee", "Restaurant Owner", "Shared Housing Host", "City Resident", "Home Owner", "NA", "NBDC Special Advisor Applicant", "Tobacco Retailer", "Parent"], "y": [126, 101, 84, 45, 31, 9, 8, 5, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2], "text": [126, 101, 84, 45, 31, 9, 8, 5, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2], "textposition": "outside", "opacity": 1}], {"title": "<b>Dept. of Business Affairs and Consumer<br>Protection Persona Appearances</b><br>", "xaxis": {"title": "", "tickfont": {"size": 11, "color": "rgb(107, 107, 107)"}}, "yaxis": {"title": "", "titlefont": {"size": 16, "color": "rgb(107, 107, 107)"}, "tickfont": {"size": 14, "color": "rgb(107, 107, 107)"}}}, {"showLink": true, "linkText": "Export to plot.ly"})});</script>

