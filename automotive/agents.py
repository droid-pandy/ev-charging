import logging
import os
import json
import boto3
from decimal import Decimal
from typing import Any, List
from datetime import datetime
from strands.models import BedrockModel
from strands import Agent
from strands.tools import tool
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "us-west-2")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super().default(obj)

def normalize_country_name(query_term):
    """Normalize country names to match database format"""
    country_mapping = {
        "germany": "Germany",
        "usa": "USA", 
        "united states": "USA",
        "america": "USA",
        "us": "USA"
    }
    return country_mapping.get(query_term.lower(), query_term.title())

def is_country_query(query_term):
    """Check if the query term might be a country name"""
    countries = ["germany", "usa", "united states", "america", "us"]
    return query_term.lower() in countries

# VISTA Agent Tools

@tool
def find_nearest_dealerships(city: str, customer_id: str = None) -> str:
    """
    Find dealerships in a specific city, with optional preferred dealer check.
    
    This tool queries the dealership database to find authorized dealerships located in the specified city.
    If a customer_id is provided, it also checks if any of the dealerships are marked as preferred
    by that customer.
    
    Args:
        city: The name of the city to search for dealerships
        customer_id: Optional customer ID to check for preferred dealers
    
    Returns:
        A JSON string containing information about authorized dealerships
    """
    try:
        city = city.title()
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        dealer_table = dynamodb.Table('Dealer_Data') 
        
        response = dealer_table.query(
            KeyConditionExpression=Key("city").eq(city)
        )
        
        items = response.get("Items", [])
        
        if not items and is_country_query(city):
            logger.info(f"No dealerships found in city {city}, trying country-based search")
            normalized_country = normalize_country_name(city)
            response = dealer_table.scan(
                FilterExpression=Attr("country").eq(normalized_country)
            )
            items = response.get("Items", [])
        
        if not items:
            if is_country_query(city):
                return json.dumps({
                    "message": f"No dealerships found in {normalize_country_name(city)}",
                    "total_count": 0,
                    "is_complete": True
                })
            else:
                return json.dumps({
                    "message": f"No dealerships found in {city}. Try searching by country if looking internationally.",
                    "total_count": 0,
                    "is_complete": True
                })
        
        dealerships = []
        preferred_dealer_name = None
        
        if customer_id:
            try:
                customer_table = dynamodb.Table('Customer_Data')
                customer_response = customer_table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('CustomerID').eq(customer_id)
                )
                
                if 'Items' in customer_response and customer_response['Items']:
                    preferred_dealer_name = customer_response['Items'][0].get('PreferredDealer')
                    logger.info(f"Found preferred dealer for customer {customer_id}: {preferred_dealer_name}")
            except Exception as e:
                logger.error(f"Error querying for preferred dealer: {str(e)}")
        
        for item in items:
            dealership = {
                "dealer_name": item.get("dealer_name"),
                "preferred_dealer": "Yes" if preferred_dealer_name and item.get("dealer_name") == preferred_dealer_name else "No",
                "city": item.get("city"),
                "website": item.get("website"),
                "street": item.get("street"),
                "state": item.get("state"),
                "country": item.get("country"),
                "zip": item.get("zip"),
                "phone": item.get("phone"),
                "email": item.get("email")
            }
            dealerships.append(dealership)
        
        return json.dumps({
            "dealerships": dealerships,
            "total_count": len(dealerships),
            "is_complete": True
        }, cls=DecimalEncoder)
        
    except ClientError as e:
        error_message = f"Error querying DynamoDB: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message, "is_complete": True})
    except Exception as e:
        error_message = f"Unexpected error occurred: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message, "is_complete": True})


@tool
def diagnose_vehicle_issues(customer_id: str = None, vin: str = None) -> str:
    """
    Diagnose vehicle issues using either a customer ID or VIN.
    
    This tool queries the Customer_Data DynamoDB table to retrieve diagnostic trouble codes (DTCs)
    and related information for a specific vehicle.
    
    Args:
        customer_id: The customer's ID to search for vehicle issues
        vin: The Vehicle Identification Number to search for issues
    
    Returns:
        A JSON string containing diagnostic information about the vehicle
    """
    try:
        if not customer_id and not vin:
            return json.dumps({
                "error": "Either customer_id or vin parameter is required for diagnosis",
                "is_complete": True
            })
        
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table('Customer_Data')
        
        dtc_results = []
        
        if customer_id:
            logger.info(f"Querying by CustomerID: {customer_id}")
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('CustomerID').eq(customer_id)
            )
            
            if 'Items' in response and response['Items']:
                for item in response['Items']:
                    if item.get('ActiveDTCCode') and item.get('DTCDescription'):
                        severity = item.get('Severity', 'unknown')
                        dtc_info = {
                            'CustomerID': item.get('CustomerID'),
                            'VehicleID': item.get('VehicleID'),
                            'Make': item.get('Make'),
                            'Model': item.get('Model'),
                            'ModelYear': item.get('ModelYear'),
                            'ActiveDTCCode': item.get('ActiveDTCCode'),
                            'DTCDescription': item.get('DTCDescription'),
                            'Severity': severity
                        }
                        dtc_results.append(dtc_info)
            
        elif vin:
            logger.info(f"Scanning by VIN: {vin}")
            response = table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('VehicleID').eq(vin)
            )
            
            if 'Items' in response and response['Items']:
                for item in response['Items']:
                    if item.get('ActiveDTCCode') and item.get('DTCDescription'):
                        severity = item.get('Severity', 'unknown')
                        dtc_info = {
                            'CustomerID': item.get('CustomerID'),
                            'VehicleID': item.get('VehicleID'),
                            'Make': item.get('Make'),
                            'Model': item.get('Model'),
                            'ModelYear': item.get('ModelYear'),
                            'ActiveDTCCode': item.get('ActiveDTCCode'),
                            'DTCDescription': item.get('DTCDescription'),
                            'Severity': severity
                        }
                        dtc_results.append(dtc_info)
        
        if dtc_results:
            return json.dumps({
                "diagnosis_results": dtc_results,
                "total_count": len(dtc_results),
                "is_complete": True
            }, cls=DecimalEncoder)
        else:
            search_term = customer_id if customer_id else vin
            search_type = 'CustomerID' if customer_id else 'VIN'
            return json.dumps({
                "message": f"No active DTC codes found for {search_type}: {search_term}",
                "is_complete": True
            })
            
    except ClientError as e:
        error_message = f"Error querying DynamoDB: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message, "is_complete": True})
    except Exception as e:
        error_message = f"Unexpected error occurred: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message, "is_complete": True})


@tool
def find_appointment_slots(dealer_name: str, appointment_date: str = None) -> str:
    """
    Find available appointment slots for a specific dealer.
    
    Args:
        dealer_name: The name of the dealer to search for appointment slots
        appointment_date: Optional specific date to search for appointments in YYYY-MM-DD format
    
    Returns:
        A JSON string containing available appointment slots
    """
    try:
        from datetime import datetime, timedelta
        
        AVAILABLE_SLOTS = [
            "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", 
            "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", 
            "04:00 PM", "05:00 PM"
        ]
        
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        appointment_table = dynamodb.Table('Dealer_Appointment_Data')
        
        if appointment_date:
            appointment_date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
            if appointment_date_obj.weekday() == 6:
                return json.dumps({
                    "error": f"The dealer is closed on Sundays. Please select another day (Monday to Saturday)."
                })
            
            today = datetime.now().strftime("%Y-%m-%d")
            if appointment_date <= today:
                return json.dumps({
                    "error": "We cannot find appointment slots for today or past dates."
                })
        
        def get_next_business_day(start_date=None):
            if start_date:
                next_day = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=1)
            else:
                next_day = datetime.now() + timedelta(days=1)
            
            while next_day.weekday() == 6:
                next_day += timedelta(days=1)
            
            return next_day.strftime("%Y-%m-%d")
        
        def format_dealer_name(dealer_name):
            if not dealer_name:
                return dealer_name
            words = dealer_name.split()
            formatted_name = ' '.join(word.capitalize() for word in words)
            return formatted_name
        
        def get_booked_appointments(dealer_name, appointment_date, appointment_table):
            formatted_dealer_name = format_dealer_name(dealer_name)
            response = appointment_table.scan(
                FilterExpression=Attr("dealer_name").eq(formatted_dealer_name) & 
                                Attr("appointment_date_time").begins_with(appointment_date)
            )
            return {item["appointment_date_time"][11:] for item in response.get("Items", [])}
        
        def find_available_slots_for_date(dealer_name, appointment_date, appointment_table):
            booked_slots = get_booked_appointments(dealer_name, appointment_date, appointment_table)
            available_slots = [
                (appointment_date, slot) for slot in AVAILABLE_SLOTS 
                if slot not in booked_slots
            ]
            return available_slots
        
        def find_available_slots(dealer_name, appointment_table):
            slots_found = []
            search_date = get_next_business_day()
            
            while len(slots_found) < 5:
                booked_slots = get_booked_appointments(dealer_name, search_date, appointment_table)
                available_slots = [
                    (search_date, slot) for slot in AVAILABLE_SLOTS 
                    if slot not in booked_slots
                ]
                
                if available_slots:
                    slots_needed = 5 - len(slots_found)
                    slots_found.extend(available_slots[:slots_needed])
                
                if len(slots_found) < 5:
                    search_date = get_next_business_day(search_date)
            
            return slots_found
        
        def get_dealer_details(dealer_name):
            dealer_table = dynamodb.Table("Dealer_Data")
            formatted_dealer_name = format_dealer_name(dealer_name)
            response = dealer_table.scan(
                FilterExpression=Attr("dealer_name").eq(formatted_dealer_name)
            )
            items = response.get("Items", [])
            if not items:
                return None
            return items[0].get("dealer_name")
        
        formatted_dealer_name = get_dealer_details(dealer_name)
        if not formatted_dealer_name:
            return json.dumps({
                "error": f"We could not find a dealer with the name '{dealer_name}'. Please check the dealer name and try again."
            })
        
        if appointment_date:
            available_slots = find_available_slots_for_date(dealer_name, appointment_date, appointment_table)
            if not available_slots:
                formatted_date = datetime.strptime(appointment_date, "%Y-%m-%d").strftime("%m-%d-%Y")
                return json.dumps({
                    "error": f"There are no available slots for the date {formatted_date}"
                })
        else:
            available_slots = find_available_slots(dealer_name, appointment_table)
        
        simplified_slots = []
        for date, time in available_slots:
            simplified_slots.append({
                "dealer_name": formatted_dealer_name,
                "appointment_date": date,
                "appointment_time": time
            })
        
        return json.dumps(simplified_slots, cls=DecimalEncoder)
        
    except ClientError as e:
        error_message = f"Error querying DynamoDB: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message})
    except Exception as e:
        error_message = f"Unexpected error occurred: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message})


@tool
def book_appointment(dealer_name: str, appointment_date: str, appointment_time: str, customer_code: str) -> str:
    """
    Book an appointment with a dealer.
    
    Args:
        dealer_name: The name of the dealer to book an appointment with
        appointment_date: The date for the appointment in YYYY-MM-DD format
        appointment_time: The time for the appointment in HH:MM AM/PM format
        customer_code: The customer's unique identifier
    
    Returns:
        A JSON string indicating whether the appointment was successfully booked
    """
    try:
        if not dealer_name or not appointment_date or not appointment_time or not customer_code:
            return json.dumps({
                "error": "Missing dealer name, appointment date, customer code or appointment time"
            })
        
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table('Dealer_Appointment_Data')
        
        appointment_date_time = f"{appointment_date} {appointment_time}"
        
        response = table.scan(
            FilterExpression=Attr('customer_code').eq(customer_code)
        )
        
        if 'Items' in response and len(response['Items']) > 0:
            return json.dumps({
                "error": "Customer already has an existing appointment"
            })
        
        item = {
            "dealer_name": dealer_name,
            "appointment_date_time": appointment_date_time,
            "customer_code": customer_code,
            "technician_code": "TECH001"
        }
        
        table.put_item(Item=item)
        
        customer_id_upper = customer_code.upper()
        customer_table = dynamodb.Table("Customer_Data")
        
        customer_email = None
        formatted_date = appointment_date
        formatted_time = appointment_time
        
        try:
            customer_response = customer_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('CustomerID').eq(customer_id_upper)
            )
            
            if 'Items' in customer_response and len(customer_response['Items']) > 0:
                customer_item = customer_response['Items'][0]
                if 'email' in customer_item:
                    customer_email = customer_item['email']
                    
                    try:
                        appointment_dt = datetime.strptime(appointment_date_time, "%Y-%m-%d %H:%M %p")
                        formatted_date = appointment_dt.strftime("%A, %B %d, %Y")
                        formatted_time = appointment_dt.strftime("%I:%M %p")
                    except Exception as format_error:
                        logger.error(f"Error formatting date/time: {str(format_error)}")
                        formatted_date = appointment_date
                        formatted_time = appointment_time
        except Exception as query_error:
            logger.error(f"Error querying customer data: {str(query_error)}")
        
        if customer_email:
            email_subject = f"Your Appointment Confirmation with {dealer_name}"
            email_body = f"""
            <html>
            <body>
                <h2>Your Appointment Has Been Booked</h2>
                <p>Dear Customer,</p>
                <p>Your appointment with {dealer_name} has been successfully booked.</p>
                <p><strong>Appointment Details:</strong></p>
                <ul>
                    <li>Date: {formatted_date}</li>
                    <li>Time: {formatted_time}</li>
                    <li>Dealer: {dealer_name}</li>
                    <li>Confirmation Code: {customer_code}</li>
                </ul>
                <p>If you need to reschedule or cancel your appointment, please contact us.</p>
                <p>Thank you for choosing our service!</p>
            </body>
            </html>
            """
            
            try:
                ses_client = boto3.client('ses', region_name=REGION)
                ses_client.send_email(
                    Source='vedev@amazon.com',
                    Destination={
                        'ToAddresses': [customer_email]
                    },
                    Message={
                        'Subject': {
                            'Data': email_subject
                        },
                        'Body': {
                            'Html': {
                                'Data': email_body
                            }
                        }
                    }
                )
                logger.info(f"Confirmation email sent to {customer_email}")
            except Exception as email_error:
                logger.error(f"Error sending email: {str(email_error)}")
        
        return json.dumps({
            "message": "appointment successfully booked"
        })
        
    except ClientError as e:
        error_message = f"Error booking appointment: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message})
    except Exception as e:
        error_message = f"Unexpected error occurred: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message})


@tool
def cancel_appointment(customer_code: str) -> str:
    """
    Cancel all appointments for a specific customer.
    
    Args:
        customer_code: The customer's unique identifier
    
    Returns:
        A JSON string indicating whether the appointments were successfully canceled
    """
    try:
        if not customer_code:
            return json.dumps({
                "error": "Missing customer code"
            })
        
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table('Dealer_Appointment_Data')
        
        response = table.scan(
            FilterExpression=Attr('customer_code').eq(customer_code)
        )
        
        if 'Items' not in response or len(response['Items']) == 0:
            return json.dumps({
                "error": "No appointments found for this customer"
            })
        
        deleted_count = 0
        
        for item in response['Items']:
            if 'dealer_name' in item and 'appointment_date_time' in item:
                table.delete_item(
                    Key={
                        'dealer_name': item['dealer_name'],
                        'appointment_date_time': item['appointment_date_time']
                    }
                )
                deleted_count += 1
        
        return json.dumps({
            "message": "appointments canceled successfully",
            "appointments_deleted": deleted_count
        })
        
    except ClientError as e:
        error_message = f"Error canceling appointment: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message})
    except Exception as e:
        error_message = f"Unexpected error occurred: {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message})


@tool
def get_customer_appointments(customer_code: str) -> str:
    """
    Get current and future appointments for a specific customer.
    Only returns appointments from today onwards.
    
    Args:
        customer_code: The customer code to search for appointments
        
    Returns:
        JSON string containing appointment details or error message
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table('Dealer_Appointment_Data')
        
        current_datetime = datetime.now()
        
        response = table.scan(
            FilterExpression=Attr('customer_code').eq(customer_code)
        )
        
        appointments = []
        for item in response['Items']:
            appointment_date_time_str = item.get('appointment_date_time', '')
            
            try:
                appointment_datetime = datetime.strptime(appointment_date_time_str, "%Y-%m-%d %I:%M %p")
                
                if appointment_datetime.date() >= current_datetime.date():
                    date_part, time_part = appointment_date_time_str.split(' ', 1)
                    
                    appointment = {
                        'dealer_name': item.get('dealer_name', 'N/A'),
                        'appointment_date': date_part,
                        'appointment_time': time_part,
                        'customer_code': item.get('customer_code', 'N/A')
                    }
                    appointments.append(appointment)
                    
            except ValueError as e:
                logger.warning(f"Could not parse appointment datetime '{appointment_date_time_str}': {str(e)}")
                continue
        
        if not appointments:
            return json.dumps({
                "status": "success",
                "message": f"No current or future appointments found for customer code: {customer_code}",
                "appointments": []
            })
        
        appointments.sort(key=lambda x: datetime.strptime(f"{x['appointment_date']} {x['appointment_time']}", "%Y-%m-%d %I:%M %p"))
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(appointments)} current/future appointment(s) for customer code: {customer_code}",
            "appointments": appointments
        })
        
    except Exception as e:
        logger.error(f"Error retrieving customer appointments: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to retrieve appointments: {str(e)}"
        })



class AgentOrchestrator:
    """Orchestrator for VISTA Agent"""
    
    def _get_system_prompt(self) -> str:
        return """You are a helpful VISTA (Vehicle Information System and Technical Assistant) agent for automotive customers.
You can help customers find the nearest authorized dealerships in a city, diagnose vehicle issues using VIN or customer ID, 
find service appointments and find parts inventory by name.

IMPORTANT!!! You are a conversational chatbot interacting with humans. So send a crisp summary of the actions you performed as output to the human.

Finding a Dealer:

When a customer asks about finding a dealership use the tool find_nearest_dealerships:
IMPORTANT: Include all the dealer information that the tool returns in the final output.

1. Ask for their city if they haven't provided it
2. If you get a valid JSON response from the tool, just simply return the dealers including all the data. Do NOT add any other dealer information.
3. Offer to help with any follow-up questions about the dealerships

Diagnose the vehicle:

When a customer asks about diagnosing vehicle issues use the tool diagnose_vehicle_issues and return the data in this format:

{ 
"message" : "Your vehicle has a trouble code P0340, which indicates a malfunction with the camshaft position sensor A circuit. This is rated as a high severity issue.
I strongly recommend booking a service appointment as soon as possible. Continuing to drive with this issue could potentially lead to further engine damage or leave you stranded.
Would you like me to help you find the nearest dealership where you can schedule a service appointment?"
}

Important: Keep your response short and sweet in less than 100 words.

1. Ask for their VIN or customer ID if they haven't provided it
2. Use the diagnose_vehicle_issues tool to retrieve diagnostic information
3. Explain the issue in simple terms, including the severity level as shortly as possible.
4. If the severity is high, strongly recommend booking a service appointment
5. If the severity is medium, suggest considering a service appointment
6. If the severity is low, inform them it's not urgent but should be addressed at their next service

Book an Appointment:

When a customer wants to book an appointment:
1. Ask for the dealer name, appointment date, appointment time, and customer code if they haven't provided them
2. Use the book_appointment tool to book the appointment
3. Send a response that the appointment has been booked successfully.

Cancel an Appointment:

When a customer wants to cancel an appointment:
1. Ask for their customer code if they haven't provided it
2. Use the cancel_appointment tool to cancel all appointments for that customer
3. Send a response that the appointment has been canceled successfully.

Find an Appointment:

When a customer asks about finding an appointment date and time use the tool find_appointment_slots and return available appointment times:

1. Ask for the dealer name and optionally a specific date.
2. If the date is in the past or on weekends, tell the user that you are not able to find appointments and ask for a new date. Do not search for any other date.
3. Use the find_appointment_slots tool to find available appointment slots.
4. Present the available slots to the human.
5. Help them select a convenient time

Get customer Appointments:

When a customer asks about details of an already booked appointment then use this tool get_customer_appointments to get details of an appointment and share that information to the human.

Be friendly, concise, and helpful in your responses. If you don't have information about a particular topic,
let the customer know and suggest alternative ways they might find that information.
"""
    
    def _get_tools(self) -> List[Any]:
        """Get all VISTA tools"""
        tools = []
        
        # Add all VISTA tools
        tools.append(find_nearest_dealerships)
        tools.append(diagnose_vehicle_issues)
        tools.append(find_appointment_slots)
        tools.append(book_appointment)
        tools.append(cancel_appointment)
        tools.append(get_customer_appointments)
        
        logger.info(f"Total tools loaded: {len(tools)}")
        logger.info(f"Tool names: {[t.__name__ for t in tools]}")
        return tools
    
    def _get_bedrock_model(self):
        """Get Bedrock model configuration"""
        return BedrockModel(
            model_id="us.amazon.nova-pro-v1:0",
            region_name=REGION,
            temperature=0.3,
            performance_config={"latency": "optimized"}
        )
    
    def create_agent(self, jwt_token: str = None) -> Agent:
        """Create the VISTA agent using the Strands SDK"""
        return Agent(
            callback_handler=None,
            model=self._get_bedrock_model(),
            system_prompt=self._get_system_prompt(),
            tools=self._get_tools()
        )
