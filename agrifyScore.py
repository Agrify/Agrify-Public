# ------------------------ LIBRARIES ----------------------------------------
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from typing import Optional
from agent import generate, format_output
# --------------------------------------------------------------------------
# ---------------Environmental Variable------------------------
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')
os.environ["TAVILY_API_KEY"] = os.getenv('TAVILY_API_KEY')

# langchain Monitoring
os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Agrifyapp"
# --------------------------------------------------------------
# -----------------------Variables------------------------------------------
DEBUG = False
# -------------------------------------------------------------------------

# ---------------------Prompt-----------------------------------------------
generator_prompt = '''
Your task is to analyze the provided farm profile data and generate a score out of 100 that reflects the farm's performance in regenerative farming practices and its ability to capture carbon. 
The score should be based on a comprehensive assessment of the soil properties and any other relevant information provided.

Soil Properties:
- Clay Content: {clay_content}
- CEC: {cec}
- Soil Depth (SOC Focus): {soil_depth}
- Silt Content: {slit_content}
- Sand Content: {sand_content}
- Soil Moisture: {soil_moisture}
- Soil pH: {soil_ph}
- Nitrogen (N) Content: {nitrogen_content}
- Area: {area}
- Bulk Density: {bulk_density}

To generate the score, please consider the following factors:

1. Soil Composition:
   - Evaluate the balance of clay, silt, and sand content in the soil and how it affects soil structure, water retention, and nutrient holding capacity.
   - Assess the soil's cation exchange capacity (CEC) and its implications for nutrient availability and soil fertility.

2. Soil Organic Carbon (SOC):
   - Analyze the soil depth at which SOC is focused and its potential impact on carbon sequestration and soil health.
   - Consider the relationship between SOC, soil moisture, and the farm's ability to retain water and maintain soil structure.

3. Soil Acidity:
   - Assess the soil's pH level and its potential impact on nutrient availability, microbial activity, and plant growth.
   - Evaluate the farm's management practices in addressing soil acidity, such as the use of lime or other amendments.

4. Nitrogen Content:
   - Analyze the nitrogen content in the soil and its adequacy for supporting plant growth and crop productivity.
   - Consider the farm's nitrogen management practices, such as the use of cover crops, compost, or other organic amendments.

5. Regenerative Farming Practices:
   - Evaluate any additional information provided about the farm's regenerative practices, such as crop rotation, cover cropping, reduced tillage, or agroforestry.
   - Assess how these practices contribute to soil health, carbon sequestration, and overall ecosystem sustainability.   

Remember: Always generate a score over 100. the score must not be over 100.
Based on your analysis of these factors, assign a score out of 100 to the farm, where a higher score indicates better performance in regenerative farming practices and carbon capture potential. 
Provide a detailed explanation of how you arrived at the score, highlighting the strengths and weaknesses of the farm's soil properties and management practices.
Your score and analysis should provide valuable insights to the farmer on areas where they are excelling and opportunities for improvement in their regenerative farming journey.
By offering a clear, evidence-based evaluation, you can help guide the farmer's decision-making and prioritization of soil health and carbon capture initiatives.
'''
reflection_prompt = """
Your task is to critically evaluate the scoring and analysis provided by the LLM in response to the farm profile data. 
The LLM was asked to generate a score out of 100 reflecting the farm's performance in regenerative farming practices and its ability to capture carbon based on the given soil properties and any additional relevant information.

Please assess the LLM's response using the following criteria:

1. Scoring Methodology:
   - Is the scoring methodology used by the LLM clear, logical, and well-justified?
   - Does the LLM provide a detailed explanation of how it arrived at the score, taking into account the various soil properties and regenerative farming practices?

2. Consideration of Soil Composition:
   - Does the LLM adequately evaluate the balance of clay, silt, and sand content in the soil and its implications for soil structure, water retention, and nutrient holding capacity?
   - Is the assessment of the soil's cation exchange capacity (CEC) and its impact on soil fertility and nutrient availability properly considered?

3. Analysis of Soil Organic Carbon (SOC):
   - Does the LLM effectively analyze the soil depth at which SOC is focused and its potential impact on carbon sequestration and soil health?
   - Is the relationship between SOC, soil moisture, and the farm's ability to retain water and maintain soil structure adequately addressed?

4. Evaluation of Soil Acidity:
   - Does the LLM properly assess the soil's pH level and its potential impact on nutrient availability, microbial activity, and plant growth?
   - Is the farm's management practices in addressing soil acidity, such as the use of lime or other amendments, taken into account?

5. Consideration of Nitrogen Content:
   - Does the LLM effectively analyze the nitrogen content in the soil and its adequacy for supporting plant growth and crop productivity?
   - Are the farm's nitrogen management practices, such as the use of cover crops, compost, or other organic amendments, properly considered?

6. Assessment of Regenerative Farming Practices:
   - Does the LLM adequately evaluate any additional information provided about the farm's regenerative practices, such as crop rotation, cover cropping, reduced tillage, or agroforestry?
   - Is the contribution of these practices to soil health, carbon sequestration, and overall ecosystem sustainability effectively assessed?

7. Clarity and Actionability of Insights:
   - Are the strengths and weaknesses of the farm's soil properties and management practices clearly highlighted in the LLM's analysis?
   - Does the LLM provide actionable insights and recommendations for the farmer to improve their regenerative farming practices and carbon capture potential?

Please provide a detailed critique of the LLM's response based on these criteria. Highlight the areas where the LLM's analysis is strong and well-supported, as well as any weaknesses or gaps in its assessment.

If there are any critical factors or considerations that the LLM has overlooked or failed to address adequately, please point these out and suggest ways to incorporate them into the scoring and analysis.

Your feedback should aim to ensure that the final score and analysis provided to the farmer are as comprehensive, accurate, and actionable as possible in guiding their regenerative farming practices and carbon capture efforts. 
By offering a rigorous and constructive evaluation of the LLM's response, you can help refine and improve the insights and recommendations provided to the farmer.
"""
generate_sys = """
You are a Streamlined Energy and Carbon reporting (SECR) Evaluator in regenerative farm for Carbon and methane capture and sequestration. 
Tasked with Evaluating based on farm profile.
If the user provides critique, develop a revised version of your previous attempts without any extra details just the report only
"""
format_instruction = """
The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

Here is the output schema:
```
{"properties": {"Score": {"title": "Score", "description": "This holds the overall score from evaluation.Please ensure it is a number and not a fraction", "type": "number"}, "Score_Breakdown_Summary": {"title": "Score Breakdown Summary", "description": "This holds the breakdown of how the score was acheived", "type": "string"}}, "required": ["Score", "Score_Breakdown_Summary"]}
```
"""
generator_prompt2 = '''
Your task is to analyze the provided farm profile data and generate a score out of 100 that reflects the farm's performance in regenerative farming practices and its ability to capture carbon. 
The score should be based on a comprehensive assessment of the soil properties and any other relevant information provided.

Soil Properties:
- Clay Content: {clay_content}
- CEC: {cec}
- Soil Depth (SOC Focus): {soil_depth}
- Silt Content: {slit_content}
- Sand Content: {sand_content}
- Soil Moisture: {soil_moisture}
- Soil pH: {soil_ph}
- Nitrogen (N) Content: {nitrogen_content}
- Area: {area}
- Bulk Density: {bulk_density}

To generate the score, please consider the following factors:

1. Soil Composition:
   - Evaluate the balance of clay, silt, and sand content in the soil and how it affects soil structure, water retention, and nutrient holding capacity.
   - Assess the soil's cation exchange capacity (CEC) and its implications for nutrient availability and soil fertility.

2. Soil Organic Carbon (SOC):
   - Analyze the soil depth at which SOC is focused and its potential impact on carbon sequestration and soil health.
   - Consider the relationship between SOC, soil moisture, and the farm's ability to retain water and maintain soil structure.

3. Soil Acidity:
   - Assess the soil's pH level and its potential impact on nutrient availability, microbial activity, and plant growth.
   - Evaluate the farm's management practices in addressing soil acidity, such as the use of lime or other amendments.

4. Nitrogen Content:
   - Analyze the nitrogen content in the soil and its adequacy for supporting plant growth and crop productivity.
   - Consider the farm's nitrogen management practices, such as the use of cover crops, compost, or other organic amendments.

5. Regenerative Farming Practices:
   - Evaluate any additional information provided about the farm's regenerative practices, such as crop rotation, cover cropping, reduced tillage, or agroforestry.
   - Assess how these practices contribute to soil health, carbon sequestration, and overall ecosystem sustainability.   

{format_instructions}   

Based on your analysis of these factors, assign a score out of 100 to the farm, where a higher score indicates better performance in regenerative farming practices and carbon capture potential. 
Provide a detailed explanation of how you arrived at the score, highlighting the strengths and weaknesses of the farm's soil properties and management practices.
Your score and analysis should provide valuable insights to the farmer on areas where they are excelling and opportunities for improvement in their regenerative farming journey.
By offering a clear, evidence-based evaluation, you can help guide the farmer's decision-making and prioritization of soil health and carbon capture initiatives.
'''


def generate_score(prompt: Optional[str] = generator_prompt, sys: Optional[str] = generate_sys,
                   reflect_sys: Optional[str] = reflection_prompt,
                   format_instruction: Optional[str] = format_instruction,
                   llm_name: Optional[str] = "llama",
                   **kwargs):

    try:
        if DEBUG:
            print(f"Using {llm_name} as llm")
            print(f"kwargs: {kwargs}")

        final_prompt = PromptTemplate.from_template(prompt)
        final_prompt = final_prompt.format(
            clay_content=kwargs["ClayContent"],
            cec=kwargs["CEC"],
            soil_depth=kwargs["SoilDepth"],
            slit_content=kwargs["SiltContent"],
            sand_content=kwargs["SandContent"],
            soil_moisture=kwargs["SoilMoisture"],
            soil_ph=kwargs["SoilPH"],
            nitrogen_content=kwargs["NitrogenContent"],
            area=kwargs["Area"],
            bulk_density=kwargs["BulkDensity"],
            format_instructions=format_instruction
        )

        gen_model = generate(sys, llm_name=llm_name)

        if DEBUG:
            print("============Generate===============")
            print("\n\n")

        result = ""
        request = HumanMessage(content=final_prompt)

        # test the single generate agent
        for chunk in gen_model.stream({"messages": [request]}):
            if DEBUG:
                print(chunk.content, end="")
            result += chunk.content

        # if reflection is activated
        if reflect_sys:
            reflect_model = generate(reflect_sys, llm_name=llm_name)
            if DEBUG:
                print("==================================")
                print("\n\n")
                print("============Reflect===============")
                print("\n\n")

            reflection = ""
            for chunk in reflect_model.stream({"messages": [request, HumanMessage(content=result)]}):
                if DEBUG:
                    print(chunk.content, end="")
                reflection += chunk.content

            report_revised = ""
            if DEBUG:
                print("==================================")
                print("\n\n")
                print("============REVISED===============")
                print("\n\n")
            for chunk in gen_model.stream({"messages": [request, AIMessage(content=result), HumanMessage(content=reflection)]}):
                if DEBUG:
                    print(chunk.content, end="")
                report_revised += chunk.content

            return report_revised

        return result
    except Exception as e:
        if DEBUG:
            print(e)

        return "Encountered an error, turn on DEBUG to see more details"


if __name__ == "__main__":
    DEBUG = False
    data = {"ClayContent": "10%",
            "CEC": "5 meq/100g",
            "SoilDepth": "Top 10 cm",
            "SiltContent": "23%",
            "SandContent": "45%",
            "SoilMoisture": "10%",
            "SoilPH": "5.0 Acidic",
            "NitrogenContent": "10 mg/kg",
            "Area": "1 hectare (10,000 m²)",
            "BulkDensity": "1.2 g/cm³"}

    result = generate_score(
        llm_name="llama",  reflect_sys=None, DEBUG=True, **data)
    formatted_result = format_output(result, "score")["Score"]
    formatted_result = int(formatted_result.split('/')[0])

    #   score = generate_score(llm_name=llm, reflect_sys=None, **data)
    #   score_result = format_output(score, "score")["Score"]
    #   score_result = int(score_result.split('/')[0])
    print(
        f"\n\n==================Final result=============\n\n{formatted_result}")


# reflect_sys=reflection_prompt, llm_name="gpt"
