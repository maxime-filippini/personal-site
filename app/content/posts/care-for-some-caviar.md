---

title: Care for some CAViaR?
posted_on: 2026-09-17
last_update: 2026-09-17
draft: false
abstract: >
    Value-at-Risk is generally estimated indirectly, either from historical observations or from an assumed distribution of returns. Conditional Autoregressive Value-at-Risk ("CAViaR") takes a different approach by modelling the conditional quantile—and therefore VaR—directly. In this post, we introduce the main CAViaR specifications, discuss their calibration, and compare their output against a common Filtered Historical Simulations approach.

---

<!-- 
Main ideas
- Historical Simulations is the most used methodology out there thanks to its
  extreme simplicity. But performance often leaves to be desired.
- Applying a filter to HS is a cheap way to boost performance by a huge amount.
- CAViaR is another way to use a relatively simple model and yield great performance
-->

Value-at-Risk is one of the most well known methods for measuring market risk. Anyone having followed a _Risk Management 101_ class will be able to tell you about it, as well as the three main methodologies used for calculating it. You would usually hear about "**Historical**", "**Parametric**" and "**Monte-Carlo**" approaches, but the truth is that all of these approaches compute the loss quantile in a roundabout way, either by making assumptions regarding direct sampling from past losses, or by estimating a full-blown distribution for future returns, from which a quantile can be computed.

Some approaches under the **Parametric** umbrella, like those based on extreme value distributions, require fewer assumptions on the central region of the returns' distribution, and instead focus on only modelling the tails. 

The **Conditional Autoregressive Value-at-Risk** methodology (abbreviated and stylized to "**CAViaR**") considers a different approach, by attempting to describe the dynamics of the quantiles of financial returns, in alignment with well known stylized facts. For example, one common formulation of the methodology is an adjustment to the GARCH model applied to quantiles, since volatility clustering leads to a similar clustering of loss quantiles. 

In this post, we explore the CAViaR methodology, how it can be estimated, and how its performance can be assessed. We will also provide a comparison to the Filtered Historical Simulations methodology, which is the cream of the crop when it comes to simple models used in the investment management industry.

## What is the CAViaR methodology?

First introduced in 2004 by Robert Engle and Simone Manganelli, the [Conditional Autoregressive Value-at-Risk](https://www.simonemanganelli.org/Simone/Research_files/caviarPublished.pdf) ("CAViaR") methodology is based on the following process:

$$
f_t(\boldsymbol{\beta}) = \beta_0 + \sum_{i=1}^q \beta_i f_{t-i}(\boldsymbol{\beta}) + \sum_{j=1}^r \beta_{q+j} l(\mathbf{x}_{t-j})
$$

where $f_t(\beta)$ represents the quantile forecast applicable at time $t$ (i.e. the VaR), based on the parameter vector $\beta$, and $l$ is a finite function of lagged values of observables. In general, we choose $\mathbf{x}_{t-j}$ to be the lagged portfolio returns (written $\{y_t\}_t$).

The CAViaR specification hinges on the definition for the function $l$, the variable $\mathbf{x}_{t-j}$, as well as a restriction on the number of parameters, via $q$ and $r$.

```note

This specification should only be considered as illustrative of the main idea. As a matter of fact, some variants of CAViaR listed below cannot be expressed cleanly in terms of said specification. Some may require the ability to have non-linear combinations of past forecasts and observables, while some others may require the involvement of multiple functions of lagged observables.

```


The original paper lists the following variants:

1. _Adaptive CAViaR_

$$
    f_t(\boldsymbol{\beta}) = f_{t-1}(\boldsymbol{\beta}) + \beta_0 \left\{\left[1+\exp\left(G\left[y_{t-1} - f_{t-1}(\boldsymbol{\beta})\right]\right)\right]^{-1}-\theta\right\}
$$

2. _Asymmetric slope ("AS") CAViaR_

$$
    f_t(\boldsymbol{\beta}) = \beta_0 
    + \beta_1 f_{t-1}(\boldsymbol{\beta})
    + \beta_2 (y_{t-1})^+
    + \beta_3 (y_{t-1})^-
$$

3. _Symmetric absolute value ("SAV") CAViaR_

$$
    f_t(\boldsymbol{\beta}) = \beta_0 
    + \beta_1 f_{t-1}(\boldsymbol{\beta})
    + \beta_2 \left|y_{t-1}\right|
$$

4. _Indirect GARCH ("IG") CAViaR_

$$
    f_t(\boldsymbol{\beta}) = \left(\beta_0 
    + \beta_1 \left(f_{t-1}(\boldsymbol{\beta})\right)^2
    + \beta_2 \left(y_{t-1}\right)^2
    \right)^{1/2}
$$

```note
For now, we will ignore the Adaptive specification, which requires an extension to the general formula provided above, and an additional choice for the parameter $G$. It is however an interesting specification, which aims to correct VaR levels directly upon the observation of an overshooting, which is a desired property.
```

To illustrate the specificities of each approach, we can use the **News Impact Curve** ("NIC"), which represents how new data affects the model's output. Because the quantile forecasts produced by these four variants only depend on the previous day's return, the NIC for a given parameter vector $\boldsymbol{\beta}$ can be plotted as a 2D graph, i.e. $y_{t-1} \mapsto f_t$. All we have to do, is assume the level of $f_{t-1}$, for example using a long-run average.

We plot these curves below, using values of $\beta$ calibrated on S&P 500 data:

![](/assets/caviar/nics.png)


As shown on these charts, small returns will lead to a decrease in the VaR forecast. In the case of the **Asymmetric Slope** specification, any positive return will lead to a decrease in VaR.

## Fitting a CAViaR model

Because CAViaR models a quantile, measuring the accuracy of the output for a given
parameter vector $\boldsymbol{\beta}$ is akin to measure the value of the following loss function:

$$
    \mathcal{L}_q: \boldsymbol{\beta} \mapsto \frac{1}{T}\sum_{t=1}^T \left[q-I(y_t < f_t(\boldsymbol{\beta}))\right]\left[y_t-f_t(\boldsymbol{\beta})\right]
$$

where $q$ represents the probability associated with the quantile being modelled.

For the 99% VaR (i.e. the 1%-quantile), the penalty associated with any observation $y_t$ for a given estimate $\hat{f_t}(\boldsymbol{\beta})$ can be written as:

$$
\mathcal{l}(y_t, \hat{f_t}(\boldsymbol{\beta})) = \begin{cases}
0.99 \times \left|y_t-\hat{f_t}(\boldsymbol{\beta})\right| &\text{if $y_t < -\hat{f_t}(\boldsymbol{\beta})$}\\
0.01 \times \left|y_t-\hat{f_t}(\boldsymbol{\beta})\right| &\text{otherwise}\\
\end{cases}
$$

The quantile estimate $\hat{f_t}(\boldsymbol{\beta})$ that minimizes this loss function will be the one so that the empirical probability mass under it (conditional on the previous information set) is equal to $q$, which is the definition of the conditional $q$-quantile, i.e.

$$
    P\left(Y_t < \hat{f_t}(\boldsymbol{\beta}) \ \middle|\ \mathcal{F}_{t-1}\right) = q
$$

The calibration procedure needed for CAViaR and proposed by Engle and Maganelli is quite complex, because of the nature of the problem at hand. The loss function defined above is non-smooth (since it cannot be differientated at the inflection point), which means numerical gradients can be noisy and solely relying on them may not lead to convergence. Naturally, one would then reach for a direct-search approach (e.g. Nelder-Mead) to attempt convergence, but these approaches can easily stall on local minima. 

The proposed approach is the following:

1. First, simulate $N$ random parameter vectors $\{\boldsymbol{\beta}_i\}_{1...N}$, using a uniform distribution $U(0,1)$ to simulate each individual value.
2. For each parameter vector, compute the total loss $\mathcal{L}_{0.01}\left(\boldsymbol{\beta_i}\right)$.
3. Select the $M$ vectors associated with the smallest losses in the set. Discard the others.
4. Run the simplex algorithm using each of these vectors as starting value.
5. Use the output of the simplex as the starting value of a Quasi-Newton algorithm.
6. Repeat step 4 until both the loss and the beta do not move by more than $10^{-10}$ (e.g. using the $L_\infty$ metric).

The local search ensure adequate coverage of the parameter space (assuming $N$ to be sufficiently large), the simplex optimization allows for finding local basins of attraction (i.e. regions of the parameter space in which a Quasi-Newton algorithm will lead to convergence), and finally, the Quasi-Newton algorithm allows to refine the estimate. The loop is there to ensure appropriate convergence.

In the original paper, the authors set the following values for $N$ and $M$:

| Approach                 | $N$    | $M$ |
| ------------------------ | ------ | --- |
| Asymmetric Slope         | $10^5$ | 15  |
| Symmetric Absolute Value | $10^4$ | 10  |
| Indirect GARCH           | $10^4$ | 10  |

A basic Python implementation of the procedure would look like this:

```python
def fit(
    approach: CaviarApproach,
    y: FloatArray,
    y_backcast: FloatArray,
    q: float,
    rng: np.random.Generator,
    n_initial_sims: int,
    m_first_pass: int,
    max_iter: int,
    tol: float,
) -> tuple[FloatArray, float]:
    """Fit a CAViaR model using returns as sole observable array.

    Args:
        approach (CaviarApproach): The CAViaR approach (e.g. IG, SAV, SA).
        y (FloatArray): Array of lagged portfolio returns.
        y_backcast (FloatArray): Array of lagged returns used to compute the starting quantile.
        q (float): The probability associated with the quantile being modelled.
        rng (np.random.Generator): Generator used for simulating random numbers.
        n_initial_sims (int): Number of initial parameter vectors to be simulated.
        m_first_pass (int): Number of parameter vectors to retain after first pass.
        max_iter (int): Maximum number of Simplex -> QN loops to perform for a given parameter vector.
        tol (float): Tolerance used for both parameter and function outputs.

    Returns:
        tuple[float, float]: Optimal (beta, loss) tuple.
    """
    # 0. Determine the CAViaR DGP and the size of the beta vector based on the
    #    selected approach.
    caviar_func = get_func(approach)
    n_params = get_n_params(approach)

    # 1. Simulate N random beta vectors sampling a U([0,1]) distribution
    cand_params = rng.uniform(0.0, 1.0, size=(n_params, n_initial_sims))

    # 2. Compute the loss for each of these vectors. Here, the `caviar_func`
    #    is written so as to run on an array of beta vectors.
    f_init = caviar_func(beta=cand_params, y=y, q=q, y_backcast=y_backcast)
    ll = compute_loss(y=y, f=f_init, q=q)

    # 3. Select the best parameters based on the M lowest loss values
    idx = np.argpartition(ll, kth=m_first_pass - 1)[:m_first_pass]
    best_params_first_pass = cand_params[:, idx]  # (n_params, m_first_pass)

    # 4. Define the objective function for the implementation. This function is
    #    responsible for computing the loss associated with a given beta vector.
    results: list[tuple[FloatArray, float]] = []
    objective = objective_func(caviar_func=caviar_func, y=y, q=q, y_backcast=y_backcast)

    # 5. We perform the optimization routine starting from all retained vectors
    for beta0 in best_params_first_pass.T:
        beta = beta0.copy()
        loss = objective(beta)

        for i_iter in range(max_iter):
            logger.info("Loop %i/(%i)", i_iter + 1, max_iter)
            beta_old = beta.copy()
            loss_old = loss

            # 5.1. Start with a Nelder-Mead pass
            nm = minimize(
                objective,
                x0=beta,
                method="Nelder-Mead",
                options={
                    "maxiter": 10000,
                    "xatol": tol,
                    "fatol": tol,
                },
            )

            # 5.2. Refine with a Quasi-Newton algorithm
            qn = minimize(
                objective,
                x0=nm.x,
                method="BFGS",
                options={
                    "maxiter": 10000,
                    "gtol": tol,
                },
            )

            beta = cast(FloatArray, qn.x)
            loss = float(qn.fun)

            # 5.3. Determine whether to continue based on pre-defined tolerance
            param_change = np.max(np.abs(beta - beta_old))
            fun_change = abs(loss - loss_old)

            logger.info("Parameter change: %e", param_change)
            logger.info("Loss change: %e", fun_change)

            if param_change < tol and fun_change < tol:
                logger.info("Convergence reached after %i iterations!", i_iter + 1)
                break

        results.append((beta, loss))

    # Keep the beta associated with the lowest overall loss
    return min(results, key=lambda x: x[1])
```

## What does it look like?

Given the cloeseness between CAViaR and Conditional Variance-based models, we take a look at the values of the three CAViaR over 2025 and H1 2026, and compare it to what is usually considered to be best-in-class: a **Filtered Historical Simulations** approach, usign a conditional variance filter (EWMA).

For simplicity, and to ensure a sufficiently conmparison period, we consider each calibration period so that VaRs can be computed from January 1st 2024.

For the CAViaR, this means the calibration period can be defined with an end date of December 31st 2023. For the Filtered Historical Simulations model, we estimate the $\lambda$ parameter using a calibration period with an end date of January 3rd 2022, which allows us to perform VaR calculations on a 500-day historical sample window starting on January 1st 2024.

We plot the VaR results for three ETFs between January 1st 2024 and June 30th 2026 (click to enlarge).

![](/assets/caviar/vars_SPY.png)
![](/assets/caviar/vars_FEZ.png)
![](/assets/caviar/vars_BND.png)
![](/assets/caviar/vars_VDE.png)

Overall, the figures show similar reactions to sharp risk increases, but the CAViaR figures show higher serial variability than the FHS model, especially for the bond ETF, as shown by the Coefficient of Variation (i.e. serial volatility divided by serialized absolute mean), plotted below:

![](/assets/caviar/var_cvs_BND.png)

## How does it compare?

Now, let us take a look at overshootings for these models over the same period. We plot below the individual occurrences of overshootings between January 1st 2024 and June 30th 2026, i.e. cases where

$$
    y_t < f_t(\boldsymbol{\beta}),
$$

along with the overall overshooting frequency for each model.

![](/assets/caviar/os_SPY.png)
![](/assets/caviar/os_FEZ.png)
![](/assets/caviar/os_BND.png)
![](/assets/caviar/os_VDE.png)

At first glance, the CAViaR models seem to lead to a similar number of overshootings as the simpler FHS specification, with the exception of the broad equity ETFs (SPY and FEZ), where the latter shows what could be a significantly higher number of overshootings. We may also wonder if the CAViaR models could be generating too few overshootings when applied to FEZ, where frequencies are closer to 0.5% than 1.0%.

Regarding SPY, it seems that the FHS model has generated mover overshootings over 2024, which was a period of relatively tame volatility. In 2025, most of the overshootings it generated were matched by overshootings for one or more of the CAViaR models.

To derive some actual conclusions, we take a look at the results of the Kupiec-POF test, using a 95% confidence level. These results are published in the table below.

| Symbol |                     Model                      |               Kupiec p-value               |         Kupiec rejection (95%)         |
| :----: | :--------------------------------------------: | :----------------------------------------: | :------------------------------------: |
|  BND   |                   caviar_AS                    |                  0.764234                  |                 false                  |
|        |                   caviar_IG                    |                  0.764234                  |                 false                  |
|        |                   caviar_SAV                   |                  0.922581                  |                 false                  |
|        |                  fhs_ewma_500                  |                  0.165543                  |                 false                  |
|  FEZ   |                   caviar_AS                    |                  0.147034                  |                 false                  |
|        |                   caviar_IG                    |                   0.3347                   |                 false                  |
|        |                   caviar_SAV                   |                   0.3347                   |                 false                  |
|        |                  fhs_ewma_500                  |                  0.084641                  |                 false                  |
|  SPY   |                   caviar_AS                    |                  0.764234                  |                 false                  |
|        |                   caviar_IG                    |                  0.764234                  |                 false                  |
|        |                   caviar_SAV                   |                  0.497437                  |                 false                  |
|        | <span class="text-red-400">fhs_ewma_500</span> | <span class="text-red-400">0.017803</span> | <span class="text-red-400">true</span> |
|  VDE   |                   caviar_AS                    |                  0.764234                  |                 false                  |
|        |                   caviar_IG                    |                  0.297638                  |                 false                  |
|        |                   caviar_SAV                   |                  0.922581                  |                 false                  |
|        |                  fhs_ewma_500                  |                  0.299635                  |                 false                  |

Solely based on that test, all models seem to be behaving appropriately, besides the FHS model applied to SPY, which generates too many overshootings.

Of course, this is only the tip of the iceberg. A full assessment of the CAViaR models would have to include the **Dynamic Quantile ("DQ") test**, introduced in the same paper, which extends the usual Christoffersen independence test by instead answering the question

> Does anything we know prior to the VaR being produced help us systematically predict whether an overshooting will happen?

This kind of test is especially important to ensure that the risk dynamics are appropriately modelled. Many models used by practicioners actually break down when the overall level of market risk increases, but then may end up generating very few overshootings in lower volatility periods.

We will look into this test and its implementation in a future post.

## Implementation code

If you want to take a look at the implementation of the functions and tools used to run CAViaR and FHS estimates, take a look at the GitHub repository, here:

[https://github.com/maxime-filippini/caviar](https://github.com/maxime-filippini/caviar)

## Conclusion

The CAViaR approach is rarely used in the asset management industry, most likely because it requires a calibration (lack of generally accepted parameters), and because its decomposition is less than straightforward (since it applies to portfolio returns).

However, it is a departure from traditional approaches in that it models VaR directly, allowing for a reduced reliance on assumptions surrounding return dynamics and distributions, while remaining relatively simple in its specification.

Risk managers' overall focus on simple models is unlikely to lead to them undertaking a multi-step calibration procedure like the one required by CAViaR. However, benchmarking those simpler models against CAViaR can bring awareness to potential modelling gains, either in terms of improved backtesting results, or of potential reductions in model risk.