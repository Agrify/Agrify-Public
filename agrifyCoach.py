#------------------------ LIBRARIES ----------------------------------------
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from typing import Optional
from agent import generate, format_output
#--------------------------------------------------------------------------

#-----------------------Variables------------------------------------------
DEBUG = False
#-------------------------------------------------------------------------

#---------------------Prompt-----------------------------------------------
# generator_prompt = '''

# Imagine you are a farmer named {farmer_name} in Nigeria who is seeking to improve your farm through regenerative practices and increase the amount of carbon captured by your farm.
# Your farm is located at {address}, and you primarily plant {crop}. To help you make informed decisions,
# you have collected soil profile and weather data for your farm over the last 3 months, which includes the following information:

# Soil Properties:
# - Clay Content: {clay_content}
# - CEC: {cec}
# - Soil Depth (SOC Focus): {soil_depth}
# - Silt Content: {slit_content}
# - Sand Content: {sand_content}
# - Soil Moisture: {soil_moisture}
# - Soil pH: {soil_ph}
# - Nitrogen (N) Content: {nitrogen_content}
# - Area: {area}
# - Bulk Density: {bulk_density}

# using this weather data
# {weather}

# Based on the provided soil profile and weather data, please suggest 9 actionable steps that {farmer_name} can take to improve soil health and regenerative farming practices on their farm over the next {duration}. 
# For each step, provide a detailed explanation of how it will benefit the farm's soil health, carbon capture potential, and overall sustainability.

# Please consider factors such as:

# 1. Soil amendments or treatments to address nutrient deficiencies or pH imbalances
# 2. Cover cropping strategies to improve soil structure, reduce erosion, and increase organic matter
# 3. Crop rotation plans to promote diversity, break pest and disease cycles, and enhance nutrient cycling
# 4. Agroforestry or silvopasture practices to increase carbon sequestration and provide additional benefits
# 5. Composting or other organic matter management techniques to boost soil fertility and microbial activity
# 6. Irrigation or water management strategies to optimize soil moisture and reduce water stress

# In your response, prioritize the most impactful and feasible actions based on the specific soil and weather conditions of {farmer_name}'s farm. Provide clear, step-by-step guidance on how to implement each recommendation, along with any necessary precautions or considerations.

# By offering tailored, evidence-based advice, you can help {farmer_name} make meaningful progress towards their goals of improving soil health, increasing carbon capture, and adopting regenerative farming practices on their farm in Nigeria.
# '''
generator_prompt = '''

Imagine you are a farmer named {farmer_name} in Nigeria who is seeking to improve your farm through regenerative practices and increase the amount of carbon captured by your farm.
To help you make informed decisions,
you have collected soil profile and weather data for your farm over the last 3 months, which includes the following information:

Soil Properties:
- Clay Content: {clay_content}
- CEC: {cec}
- Soil Depth (SOC Focus): {soil_depth}
- Silt Content: {slit_content}
- Sand Content: {sand_content}
- Soil Moisture: {soil_moisture}
- Soil pH: {soil_ph}
- Nitrogen (N) Content: {nitrogen_content}
- Bulk Density: {bulk_density}


Based on the provided soil profile and weather data, please suggest 9 actionable steps that {farmer_name} can take to improve soil health and regenerative farming practices on their farm over the next 3 months. 
For each step, provide a detailed explanation of how it will benefit the farm's soil health, carbon capture potential, and overall sustainability.

Please consider factors such as:

1. Soil amendments or treatments to address nutrient deficiencies or pH imbalances
2. Cover cropping strategies to improve soil structure, reduce erosion, and increase organic matter
3. Crop rotation plans to promote diversity, break pest and disease cycles, and enhance nutrient cycling
4. Agroforestry or silvopasture practices to increase carbon sequestration and provide additional benefits
5. Composting or other organic matter management techniques to boost soil fertility and microbial activity
6. Irrigation or water management strategies to optimize soil moisture and reduce water stress

In your response, prioritize the most impactful and feasible actions based on the specific soil and weather conditions of {farmer_name}'s farm. Provide clear, step-by-step guidance on how to implement each recommendation, along with any necessary precautions or considerations.

By offering tailored, evidence-based advice, you can help {farmer_name} make meaningful progress towards their goals of improving soil health, increasing carbon capture, and adopting regenerative farming practices on their farm in Nigeria.
'''
reflection_prompt = """
As a SECR Reviewer, your task is to critically evaluate the response provided about improving soil health and regenerative farming practices. 
Please assess the response using the following criteria:

1. Relevance and Specificity:
   - Are the suggested actionable steps relevant to the specific soil properties and weather conditions provided?
   - Does the response take into account the primary crop planted on the farm and the farm's location?

2. Feasibility and Practicality:
   - Are the recommended actions feasible for the farmer to implement within the given 3-month timeframe?
   - Does the response consider the potential limitations or constraints the farmer may face, such as access to resources or labor?

3. Explanations and Justifications:
   - Does the response provide clear and detailed explanations for each suggested step?
   - Are the benefits of each action for soil health, carbon capture potential, and overall sustainability adequately justified?

4. Prioritization and Impact:
   - Does the response prioritize the most impactful actions based on the specific soil and weather conditions of the farm?
   - Are the suggested steps likely to lead to significant improvements in soil health and carbon capture within the 3-month period?

5. Clarity and Coherence:
   - Is the response well-structured, easy to follow, and free of ambiguity?
   - Does the response use language that is accessible and understandable for the farmer?

6. Precautions and Considerations:
   - Does the response include any necessary precautions or considerations for implementing the suggested actions?
   - Are there any potential risks or unintended consequences that the response should address?

7. Evidence-based Recommendations:
   - Are the suggested steps grounded in scientific evidence or best practices for regenerative farming?
   - Does the response draw upon relevant research or case studies to support its recommendations?

Please provide a detailed critique of the LLM's response based on these criteria. Highlight the strengths and weaknesses of the response, and offer constructive feedback on how it could be improved to better meet the farmer's needs and goals.

If there are any critical aspects or considerations that the response has overlooked or failed to address adequately, please point these out and suggest ways to incorporate them.

Your feedback should aim to ensure that the final recommendations provided to the farmer are as comprehensive, practical, and effective as possible in helping them improve soil health, increase carbon capture, and adopt regenerative farming practices on their farm.
"""
generate_sys = """
You are a Streamlined Energy and Carbon reporting (SECR) Consultant in regenerative farm for Carbon and methane capture and sequestration. 
Tasked with consultation based on farmer's profile.
If the user provides critique, develop a revised version of your previous attempts without any extra details just the report only
Give your response only in {language},
"""

def recommend(prompt: Optional[str] = generator_prompt, sys: Optional[str] = generate_sys,
                    reflect_sys: Optional[str] = reflection_prompt, llm_name: Optional[str] = "llama",
                    language: Optional[str] = "English", 
                    **kwargs):
    
    try:
        if DEBUG:
            print(f"Using {llm_name} as llm")

        final_prompt = PromptTemplate.from_template(prompt)
        final_prompt = final_prompt.format(
            farmer_name = kwargs["FarmerName"],
            # address = kwargs["address"],
            # crop = kwargs["crop"],
            clay_content = kwargs["ClayContent"],
            cec = kwargs["CEC"],
            soil_depth = kwargs["SoilDepth"],
            slit_content = kwargs["SiltContent"],
            sand_content = kwargs["SandContent"],
            soil_moisture = kwargs["SoilMoisture"],
            soil_ph = kwargs["SoilPH"],
            nitrogen_content = kwargs["NitrogenContent"],
            # area = kwargs["Area"],
            bulk_density = kwargs["BulkDensity"],
            # weather = kwargs["weather"],
            # duration = kwargs["duration"],
        )

        system = PromptTemplate.from_template(sys)
        system = system.format(language = language)
        gen_model = generate(system, llm_name=llm_name)
        
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

        #if reflection is activated
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
            for chunk in gen_model.stream({"messages": [request,AIMessage(content=result),HumanMessage(content=reflection)]}):
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
    DEBUG = True
    data = {"farmer_name" : "Femi", 
    "address" :"Green field farms, ajinkoko avenue" ,
    "crop": "cassava",
    "clay_content" : "10%",
    "cec": "5 meq/100g",
    "soil_depth": "Top 10 cm",
    "slit_content": "23%",
    "sand_content" : "45%",
    "soil_moisture" : "10%",
    "soil_ph": "5.0 Acidic",
    "nitrogen_content": "10 mg/kg",
    "area": "1 hectare (10,000 m²)",
    "bulk_density": "1.2 g/cm³",
    "weather": "Rainy",
    "duration": "3 months"}

    result = recommend(generator_prompt, sys=generate_sys, 
                       reflect_sys=reflection_prompt, llm_name="gemini", 
                       language="English", **data)
    formatted_result = format_output(result, "recommend")
    print(f"\n\n==================Final result=============\n\n{formatted_result}")

#------------------------------Appendix------------------------------------
#
# farmer_name,
# address,
# crop,
# clay_content,
# cec,
# soil_depth,
# slit_content,
# sand_content,
# soil_moisture,
# soil_ph,
# nitrogen_content,
# area,
# bulk_density,
# weather,
#
#
# farmer_name: Optional[str] = kwargs.get("farmer_name")
# address: Optional[str] = kwargs.get("address")
# crop: Optional[str] = kwargs.get("crop")
# clay_content: Optional[float] = kwargs.get("clay_content")
# cec: Optional[float] = kwargs.get("cec")
# soil_depth: Optional[float] = kwargs.get("soil_depth")
# silt_content: Optional[float] = kwargs.get("slit_content")
# sand_content: Optional[float] = kwargs.get("sand_content")
# soil_moisture: Optional[float] = kwargs.get("soil_moisture")
# soil_ph: Optional[float] = kwargs.get("soil_ph")
# nitrogen_content: Optional[float] = kwargs.get("nitrogen_content")
# area: Optional[float] = kwargs.get("area")
# bulk_density: Optional[float] = kwargs.get("bulk_density")
# weather: Optional[str] = kwargs.get("weather")