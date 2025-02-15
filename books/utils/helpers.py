import stripe

from decouple import config

stripe.api_key = config('STRIPE_SECRET_KEY_TEST')


def create_token_payment(
    price_ids,
    customer_email
):
    """
    Creates and confirms a payment using a Stripe token.
    
    Args:
        price_ids: Single price_id string or list of price_ids
        token: Stripe token (starts with 'tok_')
        customer_email: Optional customer email for receipt
    
    Returns:
        dict: Payment result with status and details
    """
    try:
        TEST_TOKENS = {
            'success': 'tok_visa',
            'decline': 'tok_chargeDeclined',
            '3d_secure': 'tok_threeDSecure',
        }
        token=TEST_TOKENS['success'],

        # Convert single price_id to list
        if isinstance(price_ids, str):
            price_ids = [price_ids]
            
        # Calculate total amount
        total_amount = 0
        for price_id in price_ids:
            price = stripe.Price.retrieve(price_id)
            total_amount += price.unit_amount
        
        print(f"Total charge amount: {total_amount} cents")

        # Create a PaymentMethod from the token
        # payment_method = stripe.PaymentMethod.create(
        #     type="card",
        #     card={'token': token},
        # )
        
        # print('Payment method created:', payment_method.id)

        # Create PaymentIntent
        payment_intent_params = {
            "amount": total_amount,
            "currency": "usd",
            "payment_method": 'pm_card_visa',
            "payment_method_types": ["card"],
            "confirm": True,
            "metadata": {"price_ids": ','.join(price_ids)}
        }

        # Add email only if provided
        if customer_email:
            payment_intent_params["receipt_email"] = customer_email

        payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
        print(payment_intent.id)
        return {
            "status": "success",
            "payment_intent_id": payment_intent.id,
            "amount_paid": payment_intent.amount / 100,
        }

    except stripe.error.CardError as e:
        return {"status": "error", "message": f"Card error: {str(e)}"}
    except stripe.error.InvalidRequestError as e:
        return {"status": "error", "message": f"Invalid request: {str(e)}"}
    except stripe.error.AuthenticationError as e:
        return {"status": "error", "message": f"Authentication error: {str(e)}"}
    except stripe.error.StripeError as e:
        return {"status": "error", "message": f"Stripe error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
